"""Esquemas Pydantic para espacios (entrada y salida)."""

from pydantic import BaseModel, Field


class EspacioBase(BaseModel):
    nombre_espacio: str
    capacidad_maxima: int = Field(..., ge=1, le=300)


class EspacioCreate(EspacioBase):
    pass


class EspacioRead(EspacioBase):
    id_espacio: int

    model_config = {
        "from_attributes": True
    }
