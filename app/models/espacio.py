"""Modelo ORM de espacios para persistencia y relaciones."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Espacio(Base):
    __tablename__ = "espacio"

    id_espacio: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_espacio: Mapped[str] = mapped_column(String, nullable=False)
    capacidad_maxima: Mapped[int] = mapped_column(Integer, nullable=False)

    eventos = relationship("EventoReservacion", back_populates="espacio")
