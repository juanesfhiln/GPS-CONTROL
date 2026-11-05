
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

    if "correo" in cambios:
        existente = db.query(User).filter(
            User.correo == cambios["correo"],
            User.id != usuario.id
        ).first()

        if existente:
            raise ValueError("El correo ya está registrado")

    if "rol_id" in cambios:
        rol = db.query(Role).filter(
            Role.id == cambios["rol_id"]
        ).first()

        if not rol:
            raise ValueError("El rol seleccionado no existe")

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)

    return usuario


def cambiar_estado_usuario(db: Session, usuario):
    usuario.activo = not usuario.activo

    db.commit()
    db.refresh(usuario)

    return usuario
