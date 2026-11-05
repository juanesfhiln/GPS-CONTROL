
import os

from app.db.database import SessionLocal
from app.models import Role, User
from app.core.security import hash_password


def inicializar_datos():
    db = SessionLocal()

    try:
        # Crear roles si todavía no existen
        nombres_roles = [
            "Administrador",
            "Operador",
            "Visualizador"
        ]

        for nombre in nombres_roles:
            rol = db.query(Role).filter(
                Role.nombre == nombre
            ).first()

            if not rol:
                db.add(Role(nombre=nombre))

        db.commit()

        # Obtener los datos del administrador
        nombre = os.getenv("ADMIN_NAME")
        correo = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")

        if not nombre or not correo or not password:
            raise ValueError(
                "Faltan las variables del administrador en .env"
            )

        # Comprobar si el administrador ya existe
        administrador = db.query(User).filter(
            User.correo == correo
        ).first()

        if administrador:
            print("El administrador ya existe.")
            return

        rol_admin = db.query(Role).filter(
            Role.nombre == "Administrador"
        ).first()

        nuevo_admin = User(
            nombre=nombre,
            correo=correo,
            password_hash=hash_password(password),
            activo=True,
            cambiar_password=True,
            rol_id=rol_admin.id
        )

        db.add(nuevo_admin)
        db.commit()

        print("Administrador creado correctamente.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    inicializar_datos()
