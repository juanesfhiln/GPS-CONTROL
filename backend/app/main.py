
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import router as auth_router

app = FastAPI(
    title="GPS Control API",
    description="API para el sistema de monitoreo GPS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/api/v1"
)

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
