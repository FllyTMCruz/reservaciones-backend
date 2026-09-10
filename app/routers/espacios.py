"""Rutas HTTP relacionadas con la gestión de espacios."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.db.session import get_db
from app.models.espacio import Espacio
from app.models.usuario import RolUsuarioEnum
from app.schemas.espacio import EspacioCreate, EspacioRead

router = APIRouter(prefix="/espacios", tags=["espacios"])

# Crear, editar y borrar espacios queda reservado a Coordinador/Administración.
# Consultar espacios disponibles debe poder hacerlo cualquier usuario autenticado.
SoloGestion = Depends(
    require_role(RolUsuarioEnum.COORDINADOR, RolUsuarioEnum.ADMINISTRACION)
)


@router.get("/", response_model=list[EspacioRead])
def listar_espacios(db: Annotated[Session, Depends(get_db)]):
    """Lista todos los espacios disponibles para reservar."""
    return db.query(Espacio).all()


@router.get("/{id_espacio}", response_model=EspacioRead)
def obtener_espacio(id_espacio: int, db: Annotated[Session, Depends(get_db)]):
    """Obtiene el detalle de un espacio por su id."""
    espacio = db.get(Espacio, id_espacio)
    if espacio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Espacio no encontrado")
    return espacio


@router.post(
    "/",
    response_model=EspacioRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[SoloGestion],
)
def crear_espacio(data: EspacioCreate, db: Annotated[Session, Depends(get_db)]):
    """Crea un nuevo espacio (solo Coordinador/Administración)."""
    espacio = Espacio(**data.model_dump())
    db.add(espacio)
    db.commit()
    db.refresh(espacio)
    return espacio


@router.put(
    "/{id_espacio}",
    response_model=EspacioRead,
    dependencies=[SoloGestion],
)
def actualizar_espacio(
    id_espacio: int, data: EspacioCreate, db: Annotated[Session, Depends(get_db)]
):
    """Reemplaza los datos de un espacio existente (solo Coordinador/Administración)."""
    espacio = db.get(Espacio, id_espacio)
    if espacio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Espacio no encontrado")

    for campo, valor in data.model_dump().items():
        setattr(espacio, campo, valor)

    db.commit()
    db.refresh(espacio)
    return espacio


@router.delete(
    "/{id_espacio}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[SoloGestion],
)
def eliminar_espacio(id_espacio: int, db: Annotated[Session, Depends(get_db)]):
    """Elimina un espacio (solo Coordinador/Administración).

    Nota: la FK de evento_reservacion hacia espacio usa ondelete='RESTRICT',
    así que la base de datos rechazará el borrado si el espacio tiene
    eventos asociados. Aquí se traduce ese error en un 409 claro.
    """
    espacio = db.get(Espacio, id_espacio)
    if espacio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Espacio no encontrado")

    try:
        db.delete(espacio)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No se puede eliminar: el espacio tiene reservaciones asociadas",
        ) from exc