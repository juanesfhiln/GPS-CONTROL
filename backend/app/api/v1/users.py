
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.user import User
from app.api.dependencies import require_roles
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import (
    crear_usuario,
    obtener_usuarios,
    obtener_usuario,
    actualizar_usuario,
    cambiar_estado_usuario
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
    db: Session = Depends(get_db),
    usuario_actual: User = Depends(
        require_roles("Administrador")
    )
):
    try:
        usuario = crear_usuario(db, datos)
        return convertir_usuario(usuario)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.put("/{usuario_id}", response_model=UserResponse)
def modificar_usuario(
    usuario_id: int,
    datos: UserUpdate,
    db: Session = Depends(get_db),
    usuario_actual: User = Depends(
        require_roles("Administrador")
    )
):
    usuario = obtener_usuario(db, usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    try:
        return convertir_usuario(actualizar_usuario(db, usuario, datos))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.patch("/{usuario_id}/estado", response_model=UserResponse)
def cambiar_estado(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: User = Depends(
        require_roles("Administrador")
    )
):
    usuario = obtener_usuario(db, usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.id == usuario_actual.id:
        raise HTTPException(
            status_code=400,
            detail="No puedes cambiar el estado de tu propia cuenta"
        )

    return convertir_usuario(cambiar_estado_usuario(db, usuario))