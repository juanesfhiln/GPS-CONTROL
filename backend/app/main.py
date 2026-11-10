from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, users, vehicles, dashboard, drivers, passengers, trips, audit
from app.core.csrf import verificar_csrf, ALLOWED_ORIGINS
from app.services.vehicle_service import vehicle_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar conexión con Wialon
    await vehicle_service.wialon_client.iniciar()

    yield

    # Cerrar conexión con Wialon
    await vehicle_service.wialon_client.cerrar()

app = FastAPI(lifespan=lifespan, docs_url=None)

@app.get("/docs", include_in_schema=False)
async def swagger_documentacion():
    swagger_html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI"
    )

    contenido = swagger_html.body.decode("utf-8")

    configuracion_original = "url: '/openapi.json',"

    configuracion_csrf = """
        url: '/openapi.json',
        requestInterceptor: (request) => {
            const metodo = (request.method || "GET").toUpperCase();

            if (!["GET", "HEAD", "OPTIONS"].includes(metodo)) {
                const csrfCookie = document.cookie
                    .split("; ")
                    .find((cookie) => cookie.startsWith("csrf_token="));

                if (csrfCookie) {
                    request.headers = request.headers || {};

                    request.headers["X-CSRF-Token"] = decodeURIComponent(
                        csrfCookie.split("=").slice(1).join("=")
                    );
                }
            }

            return request;
        },
    """

    if configuracion_original not in contenido:
        raise RuntimeError(
            "No se pudo configurar el interceptor CSRF de Swagger"
        )

    contenido = contenido.replace(
        configuracion_original,
        configuracion_csrf,
        1
    )

    return HTMLResponse(content=contenido)

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
app.include_router(drivers.router, prefix="/api/v1")
app.include_router(passengers.router, prefix="/api/v1")
app.include_router(trips.router,prefix="/api/v1/trips", tags=["Historial de viajes"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Auditoría"])

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