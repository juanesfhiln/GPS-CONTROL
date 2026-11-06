
from fastapi import (
    Depends,
    HTTPException,
    status,
    Cookie,
    Request
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from app.db.dependencies import get_db
from app.models.user import User
from app.core.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db)
) -> User:

    token = access_token

    # Mantener compatibilidad con autenticación Bearer.
    if credentials is not None:
        token = credentials.credentials

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó un token de autenticación"
        )

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        token_version = payload.get("version_token")

        if not isinstance(token_version, int) or isinstance(token_version, bool):
            raise ValueError("Versión de token inválida")

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    usuario = db.query(User).filter(
        User.id == user_id
    ).first()

    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inexistente o inactivo"
        )

    # Comprobar si el token fue revocado.
    if token_version != usuario.version_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ha sido revocada"
        )

    # Permitir únicamente las rutas necesarias para cambiar la contraseña.
    rutas_permitidas = {
        "/api/v1/auth/me",
        "/api/v1/auth/change-password",
        "/api/v1/auth/logout"
    }

    if (
        usuario.cambiar_password
        and request.url.path not in rutas_permitidas
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes cambiar tu contraseña antes de continuar."
        )

    return usuario


def require_roles(*roles_permitidos: str):

    def verificar_rol(
        usuario: User = Depends(get_current_user)
    ) -> User:

        if usuario.rol.nombre not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta operación"
            )

        return usuario

    return verificar_rol
