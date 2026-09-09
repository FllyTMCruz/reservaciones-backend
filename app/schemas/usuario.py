"""Esquemas Pydantic para usuarios (entrada y salida)."""

from uuid import UUID
from pydantic import BaseModel, EmailStr

from app.models.usuario import RolUsuarioEnum


class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    rol: RolUsuarioEnum


class UsuarioCreate(UsuarioBase):
    pass


class UsuarioRead(UsuarioBase):
    id_usuario: UUID

    model_config = {
        "from_attributes": True
    }
