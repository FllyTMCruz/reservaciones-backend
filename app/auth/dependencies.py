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

from app.core.config import settings
from app.models.usuario import RolUsuarioEnum

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> dict:
    """Decodifica y valida el JWT de Supabase; devuelve el payload del token.

    La validación se hace localmente (verificando la firma con el JWT
    Secret del proyecto Supabase), sin llamar a la red en cada request.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False}, # <--- Desactivamos la verificación estricta de aud
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return payload


def get_current_user_id(
    payload: Annotated[dict, Depends(get_current_user)],
) -> UUID:
    """Extrae el id_usuario (UUID) del token ya validado.

    Este UUID coincide con auth.users.id de Supabase, que es el mismo
    id_usuario usado como PK en la tabla `usuario`.
    """
    return UUID(payload["sub"])


def require_role(*roles_permitidos: RolUsuarioEnum):
    """Fábrica de dependencias para restringir un endpoint a ciertos roles.

    El rol del usuario se espera en user_metadata.rol dentro del JWT
    (configurado al momento del signup/login en Supabase).

    Uso:
        @router.post("/", dependencies=[Depends(require_role(RolUsuarioEnum.ADMINISTRACION))])
    """

    def _checker(payload: Annotated[dict, Depends(get_current_user)]) -> dict:
        rol_valor = payload.get("user_metadata", {}).get("rol")
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
