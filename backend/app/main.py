from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, users, vehicles, dashboard
from app.core.csrf import verificar_csrf, ALLOWED_ORIGINS
from app.services.vehicle_service import vehicle_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar conexión con Wialon
    await vehicle_service.wialon_client.iniciar()

    yield

    # Cerrar conexión con Wialon
    await vehicle_service.wialon_client.cerrar()

app = FastAPI(lifespan=lifespan)

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

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(vehicles.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")


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