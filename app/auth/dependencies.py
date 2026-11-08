"""Dependencias de autenticación reutilizables para los endpoints.

Valida los JWT emitidos por Supabase Auth (login del frontend) y expone
dependencias de FastAPI para proteger rutas por usuario autenticado o por
rol (Cliente / Coordinador / Administración).
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.usuario import RolUsuarioEnum, Usuario

bearer_scheme = HTTPBearer()
optional_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.get_unverified_claims(token)
    except JWTError as exc:
        print("--- ERROR DE JWT ENCONTRADO ---")
        print(type(exc), exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido o expirado: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return payload


def get_current_user_id(
    payload: Annotated[dict, Depends(get_current_user)],
) -> UUID:
    """Extrae el id_usuario (UUID) del token ya validado."""
    return UUID(payload["sub"])


def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_bearer_scheme)],
) -> dict | None:
    """Permite lectura pública pero extrae usuario si viene un token válido."""
    if credentials is None:
        return None
    try:
        return jwt.get_unverified_claims(credentials.credentials)
    except JWTError:
        return None


def get_optional_user_id(
    payload: Annotated[dict | None, Depends(get_optional_user)],
) -> UUID | None:
    """Extrae el id_usuario opcional si el visitante está autenticado."""
    if payload is None or "sub" not in payload:
        return None
    try:
        return UUID(payload["sub"])
    except (ValueError, TypeError):
        return None


def require_role(*roles_permitidos: RolUsuarioEnum):
    """Fábrica de dependencias para restringir un endpoint a ciertos roles."""

    def _checker(
        payload: Annotated[dict, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> dict:
        usuario_db = db.get(Usuario, UUID(payload["sub"]))
        if usuario_db is not None:
            rol_usuario = usuario_db.rol
        else:
            rol_valor = (
                payload.get("user_metadata", {}).get("rol")
                or RolUsuarioEnum.CLIENTE.value
            )
            try:
                rol_usuario = RolUsuarioEnum(rol_valor)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="El token no tiene un rol válido asignado",
                ) from exc

        if rol_usuario not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para esta acción",
            )
        return payload

    return _checker
