"""Esquemas Pydantic para eventos de reservación (entrada y salida)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.evento_reservacion import EstadoEventoEnum


class EventoReservacionBase(BaseModel):
    id_espacio: int
    fecha_inicio: datetime
    fecha_fin: datetime
    tipo_evento: str = Field(..., max_length=100)
    invitados_estimados: int = Field(..., ge=1, le=300)

    @model_validator(mode="after")
    def check_dates(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return self


class EventoReservacionCreate(EventoReservacionBase):
    """Lo que manda el cliente al crear una reservación.

    id_usuario NO se recibe aquí: sale del JWT validado (ver
    get_current_user_id en el router). estado_evento tampoco se recibe:
    todo evento nuevo nace en 'Pendiente'.
    """


class EventoReservacionUpdate(BaseModel):
    """Todos los campos opcionales: solo se actualiza lo que se envía."""

    id_espacio: int | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    tipo_evento: str | None = Field(default=None, max_length=100)
    invitados_estimados: int | None = Field(default=None, ge=1, le=300)


class EventoReservacionCambiarEstado(BaseModel):
    """Body dedicado para cambiar el estado (Confirmado / Cancelado).

    Separado de Update a propósito: cambiar el estado es una acción de
    Coordinador/Administración, mientras que editar fecha/tipo/invitados
    puede quedarle permitido al dueño de la reservación.
    """

    estado_evento: EstadoEventoEnum


class EventoReservacionRead(EventoReservacionBase):
    id_evento: int
    id_usuario: UUID
    estado_evento: EstadoEventoEnum

    model_config = {"from_attributes": True}