
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import (
    verify_password,
    create_access_token
)


def authenticate_user(
    db: Session,
    correo: str,
    password: str
):
    usuario = (
        db.query(User)
        .filter(User.correo == correo)
        .first()
    )

    if not usuario:
        return None

    if not usuario.activo:
        return None

    if not verify_password(password, usuario.password_hash):
        return None

    token = create_access_token({
        "sub": str(usuario.id),
        "rol": usuario.rol.nombre
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol.nombre
    }
