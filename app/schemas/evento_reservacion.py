"""Esquemas Pydantic para eventos de reservación (entrada y salida)."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, model_validator

from app.models.evento_reservacion import EstadoEventoEnum


class EventoReservacionBase(BaseModel):
    id_usuario: UUID
    id_espacio: int
    fecha_inicio: datetime
    fecha_fin: datetime
    tipo_evento: str = Field(..., max_length=100)
    invitados_estimados: int = Field(..., ge=1, le=300)
    estado_evento: EstadoEventoEnum

    @model_validator(mode="after")
    def check_dates(cls, values):
        if values.fecha_fin <= values.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return values


class EventoReservacionCreate(EventoReservacionBase):
    pass


class EventoReservacionRead(EventoReservacionBase):
    id_evento: int

    model_config = {
        "from_attributes": True
    }
