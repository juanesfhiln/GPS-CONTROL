
import os

from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash


# Cargar configuración
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not JWT_SECRET_KEY:
    raise RuntimeError("Falta configurar JWT_SECRET_KEY")


# Configuración de contraseñas
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(password, hashed_password)


# Generación de tokens
def create_access_token(data: dict) -> str:
    datos_token = data.copy()

    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    datos_token.update({"exp": expiration})

    token = jwt.encode(
        datos_token,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token


# Validación de tokens
def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM]
    )
