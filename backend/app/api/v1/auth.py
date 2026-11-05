
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import authenticate_user


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=LoginResponse)
def login(
    datos: LoginRequest,
    db: Session = Depends(get_db)
):
    resultado = authenticate_user(
        db,
        datos.correo,
        datos.password
    )

    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return resultado
