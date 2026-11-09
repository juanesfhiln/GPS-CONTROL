from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.auth import LoginRequest
from app.services.auth_service import authenticate_user, cambiar_password_usuario
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.password import PasswordChange
from app.core.csrf import generar_csrf_token
from app.services.audit_service import audit_service

from app.core.security import (
    COOKIE_SECURE,
    COOKIE_SAMESITE,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login")
def login(
    datos: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    direccion_ip = request.client.host if request.client else None

    resultado = authenticate_user(
        db,
        datos.correo,
        datos.password
    )

    if resultado is None:
        audit_service.registrar(
            db=db,
            usuario_id=None,
            accion="LOGIN",
            modulo="AUTENTICACION",
            descripcion="Intento de inicio de sesión fallido",
            resultado="FALLIDO",
            direccion_ip=direccion_ip
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    usuario = db.query(User).filter(
        User.correo == datos.correo
    ).first()

    audit_service.registrar(
        db=db,
        usuario_id=usuario.id,
        accion="LOGIN",
        modulo="AUTENTICACION",
        descripcion="Inicio de sesión exitoso",
        resultado="EXITOSO",
        direccion_ip=direccion_ip
    )

    max_age = ACCESS_TOKEN_EXPIRE_MINUTES * 60

    response.set_cookie(
        key="access_token",
        value=resultado["access_token"],
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=max_age,
        path="/"
    )

    csrf_token = generar_csrf_token()

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=max_age,
        path="/"
    )

    return {
        "usuario": resultado["usuario"],
        "correo": resultado["correo"],
        "rol": resultado["rol"]
    }


@router.post("/logout")
def logout(
    response: Response,
    request: Request,
    usuario: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        usuario.version_token += 1
        db.commit()

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="LOGOUT",
            modulo="AUTENTICACION",
            descripcion="Cierre de sesión y revocación de sesiones",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            path="/"
        )

        response.delete_cookie(
            key="csrf_token",
            httponly=False,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            path="/"
        )

        return {
            "mensaje": "Todas las sesiones han sido revocadas correctamente"
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible cerrar la sesión"
        )


@router.get("/me")
def obtener_usuario_actual(
    usuario: User = Depends(get_current_user)
):
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol.nombre,
        "activo": usuario.activo,
        "cambiar_password": usuario.cambiar_password
    }


@router.post("/change-password")
def cambiar_password(
    datos: PasswordChange,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
    usuario: User = Depends(get_current_user)
):
    try:
        nuevo_token = cambiar_password_usuario(
            db=db,
            usuario=usuario,
            password_actual=datos.password_actual,
            password_nueva=datos.password_nueva
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="CHANGE_PASSWORD",
            modulo="AUTENTICACION",
            descripcion="Cambio de contraseña realizado correctamente",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        csrf_token = generar_csrf_token()

        response.set_cookie(
            key="access_token",
            value=nuevo_token,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/"
        )

        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/"
        )

        return {"mensaje": "Contraseña actualizada correctamente"}

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )