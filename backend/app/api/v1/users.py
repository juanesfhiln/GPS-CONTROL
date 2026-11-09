
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.user import User
from app.models.role import Role
from app.api.dependencies import require_roles
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.audit_service import audit_service
from app.services.user_service import (
    crear_usuario,
    obtener_usuarios,
    obtener_usuario,
    actualizar_usuario,
    cambiar_estado_usuario,
    restablecer_password_usuario
)


router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

def convertir_usuario(usuario):
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "activo": usuario.activo,
        "cambiar_password": usuario.cambiar_password,
        "rol": usuario.rol.nombre
    }

@router.get("/roles")
def listar_roles(
    db: Session = Depends(get_db),
    usuario_actual: User = Depends(
        require_roles("Administrador")
    )
):
    roles = db.query(Role).order_by(Role.id.asc()).all()

    return [
        {
            "id": rol.id,
            "nombre": rol.nombre
        }
        for rol in roles
    ]

@router.get("/", response_model=list[UserResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario_actual: User = Depends(
        require_roles("Administrador")
    )
):
    return [convertir_usuario(u) for u in obtener_usuarios(db)]



@router.post("/", response_model=UserResponse, status_code=201)
def registrar_usuario(
    datos: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: User = Depends(require_roles("Administrador"))
):
    try:
        usuario = crear_usuario(db, datos)

        audit_service.registrar(
            db=db,
            usuario_id=usuario_actual.id,
            accion="CREATE",
            modulo="USUARIOS",
            descripcion=f"Creación del usuario ID {usuario.id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return convertir_usuario(usuario)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.put("/{usuario_id}", response_model=UserResponse)
def modificar_usuario(
    usuario_id: int,
    datos: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: User = Depends(require_roles("Administrador"))
):
    usuario = obtener_usuario(db, usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    try:
        usuario_actualizado = actualizar_usuario(db, usuario, datos)

        audit_service.registrar(
            db=db,
            usuario_id=usuario_actual.id,
            accion="UPDATE",
            modulo="USUARIOS",
            descripcion=f"Modificación del usuario ID {usuario_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return convertir_usuario(usuario_actualizado)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.patch("/{usuario_id}/estado", response_model=UserResponse)
def cambiar_estado(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: User = Depends(require_roles("Administrador"))
):
    usuario = obtener_usuario(db, usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.id == usuario_actual.id:
        raise HTTPException(
            status_code=400,
            detail="No puedes cambiar el estado de tu propia cuenta"
        )

    estado_anterior = usuario.activo
    usuario_actualizado = cambiar_estado_usuario(db, usuario)

    nuevo_estado = "activado" if usuario_actualizado.activo else "desactivado"

    audit_service.registrar(
        db=db,
        usuario_id=usuario_actual.id,
        accion="CHANGE_STATUS",
        modulo="USUARIOS",
        descripcion=f"Usuario ID {usuario_id}: {'activo' if estado_anterior else 'inactivo'} a {nuevo_estado}",
        resultado="EXITOSO",
        direccion_ip=request.client.host if request.client else None
    )

    return convertir_usuario(usuario_actualizado)


@router.post("/{usuario_id}/restablecer-password")
def restablecer_password(
    usuario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario_actual: User = Depends(require_roles("Administrador"))
):
    usuario = obtener_usuario(db, usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    if usuario.id == usuario_actual.id:
        raise HTTPException(
            status_code=400,
            detail="No puedes restablecer tu propia contraseña desde esta opción"
        )

    try:
        password_temporal = restablecer_password_usuario(db, usuario)

        audit_service.registrar(
            db=db,
            usuario_id=usuario_actual.id,
            accion="RESET_PASSWORD",
            modulo="USUARIOS",
            descripcion=f"Restablecimiento de contraseña del usuario ID {usuario_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Contraseña restablecida correctamente",
            "password_temporal": password_temporal
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="No fue posible restablecer la contraseña"
        )