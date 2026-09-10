"""Rutas HTTP relacionadas con la gestión de usuarios.

La creación de usuarios NO ocurre aquí: nace automáticamente vía el
trigger de Supabase (on_auth_user_created) cuando alguien se registra
con Supabase Auth. Este router solo consulta y edita usuarios ya
existentes.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_id, require_role
from app.db.session import get_db
from app.models.usuario import RolUsuarioEnum, Usuario
from app.schemas.usuario import UsuarioCambiarRol, UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

SoloAdmin = Depends(require_role(RolUsuarioEnum.ADMINISTRACION))


def _obtener_o_404(db: Session, id_usuario: UUID) -> Usuario:
    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return usuario


@router.get("/me", response_model=UsuarioRead)
def obtener_mi_perfil(
    db: Annotated[Session, Depends(get_db)],
    id_usuario: UUID = Depends(get_current_user_id),
):
    """Perfil del usuario autenticado."""
    return _obtener_o_404(db, id_usuario)


@router.put("/me", response_model=UsuarioRead)
def actualizar_mi_perfil(
    data: UsuarioUpdate,
    db: Annotated[Session, Depends(get_db)],
    id_usuario: UUID = Depends(get_current_user_id),
):
    """Permite al usuario autenticado editar su propio nombre."""
    usuario = _obtener_o_404(db, id_usuario)
    usuario.nombre = data.nombre
    db.commit()
    db.refresh(usuario)
    return usuario


@router.get("/", response_model=list[UsuarioRead], dependencies=[SoloAdmin])
def listar_usuarios(db: Annotated[Session, Depends(get_db)]):
    """Lista todos los usuarios (solo Administración)."""
    return db.query(Usuario).all()


@router.get("/{id_usuario}", response_model=UsuarioRead, dependencies=[SoloAdmin])
def obtener_usuario(id_usuario: UUID, db: Annotated[Session, Depends(get_db)]):
    """Consulta el perfil de cualquier usuario (solo Administración)."""
    return _obtener_o_404(db, id_usuario)


@router.patch("/{id_usuario}/rol", response_model=UsuarioRead, dependencies=[SoloAdmin])
def cambiar_rol_usuario(
    id_usuario: UUID, data: UsuarioCambiarRol, db: Annotated[Session, Depends(get_db)]
):
    """Cambia el rol de un usuario existente (solo Administración)."""
    usuario = _obtener_o_404(db, id_usuario)
    usuario.rol = data.rol
    db.commit()
    db.refresh(usuario)
    return usuario