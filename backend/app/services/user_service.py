
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password


def crear_usuario(db: Session, datos):
    existente = db.query(User).filter(
        User.correo == datos.correo
    ).first()

    if existente:
        raise ValueError("El correo ya está registrado")

    rol = db.query(Role).filter(
        Role.id == datos.rol_id
    ).first()

    if not rol:
        raise ValueError("El rol seleccionado no existe")

    usuario = User(
        nombre=datos.nombre,
        correo=datos.correo,
        password_hash=hash_password(datos.password),
        activo=True,
        cambiar_password=True,
        rol=rol
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


def obtener_usuarios(db: Session):
    return db.query(User).all()


def obtener_usuario(db: Session, usuario_id: int):
    return db.query(User).filter(
        User.id == usuario_id
    ).first()



def actualizar_usuario(db: Session, usuario, datos):
    cambios = datos.model_dump(exclude_unset=True)

    if "nombre" in cambios and cambios["nombre"] is None:
        raise ValueError("El nombre no puede estar vacío")

    if "correo" in cambios:
        if cambios["correo"] is None:
            raise ValueError("El correo no puede estar vacío")

        existente = db.query(User).filter(
            User.correo == cambios["correo"],
            User.id != usuario.id
        ).first()

        if existente:
            raise ValueError("El correo ya está registrado")

    if "rol_id" in cambios:
        if cambios["rol_id"] is None:
            raise ValueError("El rol no puede estar vacío")

        rol = db.query(Role).filter(
            Role.id == cambios["rol_id"]
        ).first()

        if not rol:
            raise ValueError("El rol seleccionado no existe")

        usuario.rol = rol
        cambios.pop("rol_id")

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    # Revocar sesiones anteriores después de modificar la cuenta.
    usuario.version_token += 1

    try:
        db.commit()
        db.refresh(usuario)
        return usuario
    except Exception:
        db.rollback()
        raise




def cambiar_estado_usuario(db: Session, usuario):
    usuario.activo = not usuario.activo

    # Revocar todas las sesiones anteriores.
    usuario.version_token += 1

    try:
        db.commit()
        db.refresh(usuario)
        return usuario
    except Exception:
        db.rollback()
        raise