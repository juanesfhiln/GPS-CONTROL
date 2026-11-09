from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.db.dependencies import get_db
from app.api.v1 import users
from app.services.audit_service import audit_service
from app.core.csrf import generar_csrf_token, ALLOWED_ORIGINS


def crear_usuario(rol):
    return SimpleNamespace(
        id=1,
        nombre="Usuario de prueba",
        correo="prueba@gpscontrol.com",
        activo=True,
        cambiar_password=False,
        version_token=1,
        rol=SimpleNamespace(nombre=rol)
    )


@pytest.fixture
def cliente(monkeypatch, request):
    rol = getattr(request, "param", "Administrador")

    usuario = crear_usuario(rol)

    app.dependency_overrides[get_current_user] = lambda: usuario

    db_mock = Mock()

    app.dependency_overrides[get_db] = lambda: db_mock

    monkeypatch.setattr(
        users,
        "obtener_usuarios",
        lambda db: []
    )

    monkeypatch.setattr(
        audit_service,
        "contar",
        Mock(return_value=0)
    )

    monkeypatch.setattr(
        audit_service,
        "listar",
        Mock(return_value=[])
    )

    token = generar_csrf_token()
    origen = next(iter(ALLOWED_ORIGINS))

    with TestClient(app) as test_client:
        test_client.cookies.set("csrf_token", token)

        test_client.headers.update({
            "Origin": origen,
            "X-CSRF-Token": token
        })

        yield test_client

    app.dependency_overrides.clear()

@pytest.mark.parametrize(
    "cliente",
    ["Administrador"],
    indirect=True
)
def test_administrador_puede_listar_usuarios(cliente):
    respuesta = cliente.get("/api/v1/users/")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


@pytest.mark.parametrize(
    "rol",
    ["Operador", "Visualizador"]
)
@pytest.mark.parametrize(
    "cliente",
    ["Operador", "Visualizador"],
    indirect=True
)
def test_operador_y_visualizador_no_pueden_listar_usuarios(
    cliente,
    rol
):
    respuesta = cliente.get("/api/v1/users/")

    assert respuesta.status_code == 403

@pytest.mark.parametrize(
    "metodo,ruta",
    [
        ("get", "/api/v1/users/roles"),
        ("post", "/api/v1/users/"),
        ("put", "/api/v1/users/1"),
        ("patch", "/api/v1/users/1/estado"),
        ("post", "/api/v1/users/1/restablecer-password")
    ],
    ids=[
        "listar_roles",
        "crear_usuario",
        "actualizar_usuario",
        "cambiar_estado",
        "restablecer_password"
    ]
)
@pytest.mark.parametrize(
    "cliente",
    ["Operador", "Visualizador"],
    indirect=True
)
def test_roles_no_administrativos_no_pueden_gestionar_usuarios(
    cliente,
    metodo,
    ruta
):
    respuesta = getattr(cliente, metodo)(ruta)

    assert respuesta.status_code == 403

@pytest.mark.parametrize(
    "cliente",
    ["Administrador"],
    indirect=True
)
def test_administrador_puede_consultar_auditoria(cliente):
    respuesta = cliente.get("/api/v1/audit/")

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["total"] == 0
    assert datos["resultados"] == []


@pytest.mark.parametrize(
    "cliente",
    ["Operador", "Visualizador"],
    indirect=True
)
def test_operador_y_visualizador_no_pueden_consultar_auditoria(
    cliente
):
    respuesta = cliente.get("/api/v1/audit/")

    assert respuesta.status_code == 403

@pytest.mark.parametrize(
    "parametros",
    [
        {"pagina": 0},
        {"limite": 0},
        {"limite": 101}
    ]
)
@pytest.mark.parametrize(
    "cliente",
    ["Administrador"],
    indirect=True
)
def test_auditoria_rechaza_paginacion_invalida(
    cliente,
    parametros
):
    respuesta = cliente.get(
        "/api/v1/audit/",
        params=parametros
    )

    assert respuesta.status_code == 422

def test_endpoint_protegido_rechaza_solicitud_sin_token():
    app.dependency_overrides.clear()

    with TestClient(app) as test_client:
        respuesta = test_client.get("/api/v1/audit/")

    assert respuesta.status_code == 401
