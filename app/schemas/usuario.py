"""Esquemas Pydantic para usuarios (entrada y salida)."""

from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.usuario import RolUsuarioEnum


class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    rol: RolUsuarioEnum


class UsuarioRead(UsuarioBase):
    id_usuario: UUID

    model_config = {"from_attributes": True}


class UsuarioUpdate(BaseModel):
    """El usuario solo puede editar su propio nombre.

    correo y rol no son editables por el propio usuario: correo lo
    controla Supabase Auth, y rol solo lo cambia un Administrador
    (ver UsuarioCambiarRol).
    """

    nombre: str


class UsuarioCambiarRol(BaseModel):
    """Body dedicado para que un Administrador cambie el rol de otro usuario."""

    rol: RolUsuarioEnum