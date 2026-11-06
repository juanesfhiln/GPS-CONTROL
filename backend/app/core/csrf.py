
import hashlib
import hmac
import os
import secrets

from fastapi import Request, status
from starlette.responses import JSONResponse

from app.core.security import JWT_SECRET_KEY


CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "X-CSRF-Token"
AUTH_COOKIE_NAME = "access_token"

ALLOWED_ORIGINS = {
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173"
    ).split(",")
    if origin.strip()
}


def generar_csrf_token() -> str:
    nonce = secrets.token_urlsafe(32)

    firma = hmac.new(
        JWT_SECRET_KEY.encode("utf-8"),
        f"gps-control-csrf:{nonce}".encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"{nonce}.{firma}"


def validar_csrf_token(token: str) -> bool:
    try:
        nonce, firma_recibida = token.split(".", 1)

        if not nonce or not firma_recibida:
            return False

        firma_esperada = hmac.new(
            JWT_SECRET_KEY.encode("utf-8"),
            f"gps-control-csrf:{nonce}".encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(
            firma_esperada,
            firma_recibida
        )

    except (ValueError, AttributeError):
        return False


async def verificar_csrf(request: Request, call_next):

    if request.method in ("GET", "HEAD", "OPTIONS"):
        return await call_next(request)

    origin = request.headers.get("origin")

    # El login exige un origen autorizado.
    if request.url.path == "/api/v1/auth/login":
        if origin not in ALLOWED_ORIGINS:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Origen no permitido"}
            )

        return await call_next(request)

    # Los tokens Bearer no dependen de cookies del navegador.
    # Por tanto, no necesitan esta protección CSRF.
    authorization = request.headers.get("authorization", "")
    usa_bearer = authorization.lower().startswith("bearer ")

    access_cookie = request.cookies.get(AUTH_COOKIE_NAME)

    if usa_bearer and not access_cookie:
        return await call_next(request)

    # Para sesiones autenticadas mediante cookies,
    # exigimos origen autorizado.
    if origin not in ALLOWED_ORIGINS:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Origen no permitido"}
        )

    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    header_token = request.headers.get(CSRF_HEADER_NAME)

    if (
        not cookie_token
        or not header_token
        or not hmac.compare_digest(cookie_token, header_token)
        or not validar_csrf_token(cookie_token)
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Validación CSRF fallida"}
        )

    return await call_next(request)
