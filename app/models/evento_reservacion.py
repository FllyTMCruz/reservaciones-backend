"""Modelo ORM de eventos de reservación con relaciones a usuario y espacio."""

from enum import Enum
from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.base import Base
from app.models.usuario import RolUsuarioEnum


class EstadoEventoEnum(str, Enum):
    PENDIENTE = "Pendiente"
    CONFIRMADO = "Confirmado"
    CANCELADO = "Cancelado"


class EventoReservacion(Base):
    __tablename__ = "evento_reservacion"

    id_evento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[PGUUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    id_espacio: Mapped[int] = mapped_column(
        Integer, ForeignKey("espacio.id_espacio", ondelete="CASCADE"), nullable=False
    )
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    tipo_evento: Mapped[str] = mapped_column(String(100), nullable=False)
    invitados_estimados: Mapped[int] = mapped_column(Integer, nullable=False)
    estado_evento: Mapped[EstadoEventoEnum] = mapped_column(
        SqlEnum(EstadoEventoEnum, name="estado_evento_enum"),
        nullable=False,
    )

    usuario = relationship("Usuario", back_populates="eventos")
    espacio = relationship("Espacio", back_populates="eventos")
