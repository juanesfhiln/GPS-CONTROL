
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.db.dependencies import get_db
from app.core.csrf import generar_csrf_token, ALLOWED_ORIGINS
from app.services.vehicle_service import vehicle_service
from app.services.driver_service import driver_service
from app.services.passenger_service import passenger_service


@pytest.fixture
def cliente(monkeypatch, request):
    rol = getattr(request, "param", "Administrador")

    usuario = SimpleNamespace(
        id=1,
        rol=SimpleNamespace(nombre=rol),
        cambiar_password=False
    )

    app.dependency_overrides[get_current_user] = lambda: usuario
    app.dependency_overrides[get_db] = lambda: Mock()

    monkeypatch.setattr(
        vehicle_service.wialon_client,
        "iniciar",
        AsyncMock()
    )
    monkeypatch.setattr(
        vehicle_service.wialon_client,
        "cerrar",
        AsyncMock()
    )

    monkeypatch.setattr(
        vehicle_service,
        "obtener_vehiculos",
        AsyncMock(return_value=[])
    )
    monkeypatch.setattr(
        driver_service,
        "obtener_conductores",
        AsyncMock(return_value=[])
    )
    monkeypatch.setattr(
        driver_service,
        "obtener_asignaciones",
        AsyncMock(return_value=[])
    )
    monkeypatch.setattr(
        passenger_service,
        "obtener_pasajeros",
        AsyncMock(return_value=[])
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
    ["Administrador", "Operador", "Visualizador"],
    indirect=True
)
@pytest.mark.parametrize(
    "ruta",
    [
        "/api/v1/vehicles/",
        "/api/v1/drivers/",
        "/api/v1/drivers/asignaciones",
        "/api/v1/passengers/"
    ]
)
def test_todos_los_roles_pueden_consultar_recursos(cliente, ruta):
    respuesta = cliente.get(ruta)

    assert respuesta.status_code == 200


@pytest.mark.parametrize(
    "cliente",
    ["Administrador", "Operador"],
    indirect=True
)
@pytest.mark.parametrize(
    "metodo,ruta,datos,servicio,resultado",
    [
        (
            "put",
            "/api/v1/vehicles/123/custom-fields/1",
            {"nombre": "Placa", "valor": "ABC123"},
            "actualizar_campo_personalizado",
            True
        ),
        (
            "post",
            "/api/v1/drivers/",
            {
                "name": "Carlos Ruiz",
                "code": "CON-001",
                "phone": "3001234567",
                "description": "Conductor de prueba"
            },
            "crear_conductor",
            101
        ),
        (
            "put",
            "/api/v1/drivers/101",
            {
                "name": "Carlos Ruiz actualizado",
                "code": "CON-001",
                "phone": "3001234567",
                "description": "Conductor actualizado"
            },
            "actualizar_conductor",
            101
        ),
        (
            "delete",
            "/api/v1/drivers/101",
            None,
            "eliminar_conductor",
            101
        ),
        (
            "post",
            "/api/v1/drivers/101/asignar/12345",
            None,
            "asignar_conductor",
            True
        ),
        (
            "delete",
            "/api/v1/drivers/101/desvincular/12345",
            None,
            "desvincular_conductor",
            True
        ),
        (
            "post",
            "/api/v1/passengers/",
            {
                "name": "Ana Gómez",
                "code": "PAS-001",
                "phone": "3001234567",
                "custom_fields": {}
            },
            "crear_pasajero",
            101
        ),
        (
            "put",
            "/api/v1/passengers/101",
            {
                "name": "Ana Gómez actualizada",
                "code": "PAS-001",
                "phone": "3001234567",
                "custom_fields": {}
            },
            "actualizar_pasajero",
            101
        ),
        (
            "delete",
            "/api/v1/passengers/101",
            None,
            "eliminar_pasajero",
            101
        ),
        (
            "post",
            "/api/v1/passengers/101/asignar/12345",
            None,
            "asignar_pasajero",
            True
        ),
        (
            "delete",
            "/api/v1/passengers/101/desvincular/12345",
            None,
            "desvincular_pasajero",
            True
        )
    ]
)
def test_administrador_y_operador_pueden_modificar_recursos(
    cliente,
    monkeypatch,
    metodo,
    ruta,
    datos,
    servicio,
    resultado
):
    if servicio == "actualizar_campo_personalizado":
        objeto = vehicle_service
    elif servicio.endswith("_conductor"):
        objeto = driver_service
    else:
        objeto = passenger_service

    operacion = AsyncMock(return_value=resultado)

    monkeypatch.setattr(objeto, servicio, operacion)

    if datos is None:
        respuesta = getattr(cliente, metodo)(ruta)
    else:
        respuesta = getattr(cliente, metodo)(ruta, json=datos)

    assert respuesta.status_code in (200, 201)
    operacion.assert_awaited_once()


@pytest.mark.parametrize(
    "cliente",
    ["Visualizador"],
    indirect=True
)
@pytest.mark.parametrize(
    "metodo,ruta,datos",
    [
        (
            "put",
            "/api/v1/vehicles/123/custom-fields/1",
            {"nombre": "Placa", "valor": "ABC123"}
        ),
        (
            "post",
            "/api/v1/drivers/",
            {
                "name": "Carlos Ruiz",
                "code": "CON-001",
                "phone": "3001234567",
                "description": "Conductor de prueba"
            }
        ),
        (
            "put",
            "/api/v1/drivers/101",
            {
                "name": "Carlos Ruiz actualizado",
                "code": "CON-001",
                "phone": "3001234567",
                "description": "Conductor actualizado"
            }
        ),
        ("delete", "/api/v1/drivers/101", None),
        ("post", "/api/v1/drivers/101/asignar/12345", None),
        ("delete", "/api/v1/drivers/101/desvincular/12345", None),
        (
            "post",
            "/api/v1/passengers/",
            {
                "name": "Ana Gómez",
                "code": "PAS-001",
                "phone": "3001234567",
                "custom_fields": {}
            }
        ),
        (
            "put",
            "/api/v1/passengers/101",
            {
                "name": "Ana Gómez actualizada",
                "code": "PAS-001",
                "phone": "3001234567",
                "custom_fields": {}
            }
        ),
        ("delete", "/api/v1/passengers/101", None),
        ("post", "/api/v1/passengers/101/asignar/12345", None),
        ("delete", "/api/v1/passengers/101/desvincular/12345", None)
    ]
)
def test_visualizador_no_puede_modificar_recursos(
    cliente,
    metodo,
    ruta,
    datos
):
    if datos is None:
        respuesta = getattr(cliente, metodo)(ruta)
    else:
        respuesta = getattr(cliente, metodo)(ruta, json=datos)

    assert respuesta.status_code == 403
