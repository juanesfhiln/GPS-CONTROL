
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1 import vehicles
from app.core.csrf import verificar_csrf, ALLOWED_ORIGINS


app = FastAPI(
    title="GPS Control API",
    description="API para el sistema de monitoreo GPS",
    version="1.0.0"
)

# Middleware CSRF.
app.middleware("http")(verificar_csrf)

# CORS utiliza los mismos orígenes autorizados que CSRF.
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"]
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(vehicles.router, prefix="/api/v1")


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido a GPS Control API"
    }


@app.get("/health")
def verificar_estado():
    return {
        "status": "ok",
        "mensaje": "El backend está funcionando correctamente"
    }
