
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import (
    verify_password,
    hash_password,
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
        "rol": usuario.rol.nombre,
        "version_token": usuario.version_token
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol.nombre
    }

def cambiar_password_usuario(
    db: Session,
    usuario: User,
    password_actual: str,
    password_nueva: str
):
    if not verify_password(password_actual, usuario.password_hash):
        raise ValueError("La contraseña actual es incorrecta")

    usuario.password_hash = hash_password(password_nueva)
    usuario.cambiar_password = False
    usuario.version_token += 1

    try:
        db.commit()
        db.refresh(usuario)

        nuevo_token = create_access_token({
            "sub": str(usuario.id),
            "rol": usuario.rol.nombre,
            "version_token": usuario.version_token
        })

        return nuevo_token

    except Exception:
        db.rollback()
        raise