"""Rutas HTTP relacionadas con la gestión de eventos de reservación."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
    get_current_user_id,
    get_optional_user_id,
    require_role,
)
from app.db.session import get_db
from app.models.espacio import Espacio
from app.models.evento_reservacion import EstadoEventoEnum, EventoReservacion
from app.models.usuario import RolUsuarioEnum, Usuario
from app.schemas.evento_reservacion import (
    EventoReservacionCambiarEstado,
    EventoReservacionCreate,
    EventoReservacionRead,
    EventoReservacionUpdate,
)

router = APIRouter(prefix="/eventos", tags=["eventos"])

SoloGestion = Depends(
    require_role(RolUsuarioEnum.COORDINADOR, RolUsuarioEnum.ADMINISTRACION)
)


def _obtener_o_404(db: Session, id_evento: int) -> EventoReservacion:
    evento = db.get(EventoReservacion, id_evento)
    if evento is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evento no encontrado")
    return evento


def _es_rol_de_gestion(db: Session, payload: dict) -> bool:
    usuario_db = db.get(Usuario, UUID(payload["sub"]))
    if usuario_db is not None:
        return usuario_db.rol in (
            RolUsuarioEnum.COORDINADOR,
            RolUsuarioEnum.ADMINISTRACION,
        )
    rol_valor = payload.get("user_metadata", {}).get("rol")
    return rol_valor in (
        RolUsuarioEnum.COORDINADOR.value,
        RolUsuarioEnum.ADMINISTRACION.value,
    )


def _validar_capacidad(db: Session, id_espacio: int, invitados_estimados: int) -> None:
    espacio = db.get(Espacio, id_espacio)
    if espacio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Espacio no encontrado")
    if invitados_estimados > espacio.capacidad_maxima:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"El espacio '{espacio.nombre_espacio}' admite máximo "
            f"{espacio.capacidad_maxima} invitados",
        )


@router.get("/", response_model=list[EventoReservacionRead])
def listar_eventos(
    db: Annotated[Session, Depends(get_db)],
    id_espacio: int | None = None,
    solo_mias: bool = False,
    id_usuario_actual: UUID | None = Depends(get_optional_user_id),
):
    """Lista eventos del calendario (público). Con solo_mias=true, requiere sesión y filtra las del usuario."""
    query = db.query(EventoReservacion)
    if id_espacio is not None:
        query = query.filter(EventoReservacion.id_espacio == id_espacio)
    if solo_mias:
        if id_usuario_actual is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Debes iniciar sesión para filtrar tus reservaciones",
            )
        query = query.filter(EventoReservacion.id_usuario == id_usuario_actual)
    return query.order_by(EventoReservacion.fecha_inicio).all()


@router.get("/{id_evento}", response_model=EventoReservacionRead)
def obtener_evento(
    id_evento: int,
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict, Depends(get_current_user)],
):
    """Obtiene el detalle de un evento. Requiere autenticación (dueño o gestión)."""
    evento = _obtener_o_404(db, id_evento)
    id_usuario_actual = UUID(payload["sub"])
    if evento.id_usuario != id_usuario_actual and not _es_rol_de_gestion(db, payload):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "No puedes ver una reservación que no es tuya"
        )
    return evento


@router.post("/", response_model=EventoReservacionRead, status_code=status.HTTP_201_CREATED)
def crear_evento(
    data: EventoReservacionCreate,
    db: Annotated[Session, Depends(get_db)],
    id_usuario: UUID = Depends(get_current_user_id),
):
    """Crea una reservación. id_usuario sale del token JWT, estado_evento nace en Pendiente."""
    _validar_capacidad(db, data.id_espacio, data.invitados_estimados)
    evento = EventoReservacion(
        **data.model_dump(),
        id_usuario=id_usuario,
        estado_evento=EstadoEventoEnum.Pendiente,
    )
    db.add(evento)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if _es_error_de_traslape(exc):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Ese espacio ya está reservado en ese horario",
            ) from exc
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se pudo crear la reservación") from exc
    db.refresh(evento)
    return evento


@router.put("/{id_evento}", response_model=EventoReservacionRead)
def actualizar_evento(
    id_evento: int,
    data: EventoReservacionUpdate,
    db: Annotated[Session, Depends(get_db)],
    id_usuario_actual: UUID = Depends(get_current_user_id),
):
    evento = _obtener_o_404(db, id_evento)
    if evento.id_usuario != id_usuario_actual:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "No puedes modificar una reservación que no es tuya"
        )

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(evento, campo, valor)

    if evento.fecha_fin <= evento.fecha_inicio:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "fecha_fin debe ser posterior a fecha_inicio",
        )

    _validar_capacidad(db, evento.id_espacio, evento.invitados_estimados)

    if evento.estado_evento == EstadoEventoEnum.Confirmado:
        evento.estado_evento = EstadoEventoEnum.Pendiente

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if _es_error_de_traslape(exc):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Ese espacio ya está reservado en ese horario",
            ) from exc
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se pudo actualizar la reservación") from exc
    db.refresh(evento)
    return evento


@router.patch(
    "/{id_evento}/estado",
    response_model=EventoReservacionRead,
    dependencies=[SoloGestion],
)
def cambiar_estado_evento(
    id_evento: int,
    data: EventoReservacionCambiarEstado,
    db: Annotated[Session, Depends(get_db)],
):
    """Confirma o cancela una reservación (solo Coordinador/Administración)."""
    evento = _obtener_o_404(db, id_evento)
    evento.estado_evento = data.estado_evento
    db.commit()
    db.refresh(evento)
    return evento


@router.delete("/{id_evento}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_evento(
    id_evento: int,
    db: Annotated[Session, Depends(get_db)],
    id_usuario_actual: UUID = Depends(get_current_user_id),
):
    evento = _obtener_o_404(db, id_evento)
    if evento.id_usuario != id_usuario_actual:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "No puedes eliminar una reservación que no es tuya"
        )
    db.delete(evento)
    db.commit()


def _es_error_de_traslape(exc: IntegrityError) -> bool:
    pgcode = getattr(getattr(exc, "orig", None), "pgcode", None)
    return pgcode == "23P01"
