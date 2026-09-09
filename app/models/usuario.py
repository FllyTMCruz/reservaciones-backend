"""Modelo ORM de usuarios para persistencia y relaciones."""

from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RolUsuarioEnum(str, Enum):
    CLIENTE = "Cliente"
    COORDINADOR = "Coordinador"
    ADMINISTRACION = "Administración"


class Usuario(Base):
    __tablename__ = "usuario"

    # Este id lo emite Supabase Auth (auth.users.id), por eso no se genera en la app.
    id_usuario: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    correo: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    rol: Mapped[RolUsuarioEnum] = mapped_column(
        SqlEnum(RolUsuarioEnum, name="rol_usuario_enum"),
        nullable=False,
    )

    eventos = relationship("EventoReservacion", back_populates="usuario")
