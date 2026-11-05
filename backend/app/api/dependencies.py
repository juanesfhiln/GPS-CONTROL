
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from app.db.dependencies import get_db
from app.models.user import User
from app.core.security import decode_access_token


# Esquema para recibir el token Bearer
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:

    # Comprobar que se envió el token
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó un token de autenticación"
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload.get("sub"))

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    # Buscar el usuario en PostgreSQL
    usuario = db.query(User).filter(
        User.id == user_id
    ).first()

    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inexistente o inactivo"
        )

    return usuario


# Dependencia para controlar los roles permitidos
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
