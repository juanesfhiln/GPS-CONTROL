
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.services.passenger_service import passenger_service
from app.domain.passenger import Passenger
from app.core.csrf import generar_csrf_token, ALLOWED_ORIGINS


@pytest.fixture
def cliente(monkeypatch, request):
    rol = getattr(request, "param", "Administrador")

    usuario = SimpleNamespace(
        rol=SimpleNamespace(nombre=rol),
        cambiar_password=False
    )

    app.dependency_overrides[get_current_user] = lambda: usuario

    monkeypatch.setattr(
        passenger_service,
        "obtener_pasajeros",
        AsyncMock(return_value=[
            Passenger(
                id=101,
                name="Juan Pérez",
                code="PAS-001",
                phone="3001234567",
                assigned_unit_id=None,
                custom_fields={"Área": "Norte"}
            ),
            Passenger(
                id=102,
                name="Ana Gómez",
                code="PAS-002",
                phone="3007654321",
                assigned_unit_id=12345,
                custom_fields={}
            )
        ])
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


def test_listar_pasajeros(cliente):
    respuesta = cliente.get("/api/v1/passengers/")

    assert respuesta.status_code == 200
    assert respuesta.json()["total"] == 2
    assert len(respuesta.json()["resultados"]) == 2


def test_buscar_pasajero(cliente):
    respuesta = cliente.get(
        "/api/v1/passengers/",
        params={"buscar": "Juan"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["total"] == 1
    assert respuesta.json()["resultados"][0]["name"] == "Juan Pérez"


def test_paginacion_pasajeros(cliente):
    respuesta = cliente.get(
        "/api/v1/passengers/",
        params={"pagina": 1, "limite": 1}
    )

    datos = respuesta.json()

    assert respuesta.status_code == 200
    assert datos["total"] == 2
    assert datos["limite"] == 1
    assert len(datos["resultados"]) == 1
    assert datos["total_paginas"] == 2


def test_pagina_fuera_de_rango(cliente):
    respuesta = cliente.get(
        "/api/v1/passengers/",
        params={"pagina": 0}
    )

    assert respuesta.status_code == 422


def test_crear_pasajero(cliente, monkeypatch):
    crear = AsyncMock(return_value=201)

    monkeypatch.setattr(
        passenger_service,
        "crear_pasajero",
        crear
    )

    respuesta = cliente.post(
        "/api/v1/passengers/",
        json={
            "name": "Carlos Ruiz",
            "code": "PAS-003",
            "phone": "3009999999",
            "custom_fields": {"Área": "Centro"}
        }
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["id_wialon"] == 201
    crear.assert_awaited_once()


def test_actualizar_pasajero(cliente, monkeypatch):
    actualizar = AsyncMock(return_value=101)

    monkeypatch.setattr(
        passenger_service,
        "actualizar_pasajero",
        actualizar
    )

    respuesta = cliente.put(
        "/api/v1/passengers/101",
        json={
            "name": "Juan Pérez actualizado",
            "code": "PAS-001",
            "phone": "3001234567",
            "custom_fields": {}
        }
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["id_wialon"] == 101
    assert actualizar.await_args.kwargs["campos_personalizados"] == {}


def test_eliminar_pasajero(cliente, monkeypatch):
    eliminar = AsyncMock(return_value=101)

    monkeypatch.setattr(
        passenger_service,
        "eliminar_pasajero",
        eliminar
    )

    respuesta = cliente.delete("/api/v1/passengers/101")

    assert respuesta.status_code == 200
    assert respuesta.json()["passenger_id"] == 101
    eliminar.assert_awaited_once()


def test_error_de_validacion_del_servicio(cliente, monkeypatch):
    monkeypatch.setattr(
        passenger_service,
        "eliminar_pasajero",
        AsyncMock(side_effect=ValueError("El pasajero está asignado"))
    )

    respuesta = cliente.delete("/api/v1/passengers/101")

    assert respuesta.status_code == 409


@pytest.mark.parametrize(
    "cliente",
    ["Visualizador"],
    indirect=True
)
def test_visualizador_puede_consultar_pasajeros(cliente):
    respuesta = cliente.get("/api/v1/passengers/")

    assert respuesta.status_code == 200


@pytest.mark.parametrize(
    "cliente",
    ["Visualizador"],
    indirect=True
)
@pytest.mark.parametrize(
    "metodo, ruta, datos",
    [
        (
            "post",
            "/api/v1/passengers/",
            {
                "name": "Carlos Ruiz",
                "code": "PAS-003",
                "phone": "3009999999",
                "custom_fields": {}
            }
        ),
        (
            "put",
            "/api/v1/passengers/101",
            {
                "name": "Juan Pérez actualizado",
                "code": "PAS-001",
                "phone": "3001234567",
                "custom_fields": {}
            }
        ),
        ("delete", "/api/v1/passengers/101", None),
        ("post", "/api/v1/passengers/101/asignar/12345", None),
        ("delete", "/api/v1/passengers/101/desvincular/12345", None)
    ],
    ids=[
        "crear",
        "actualizar",
        "eliminar",
        "asignar",
        "desvincular"
    ]
)
def test_visualizador_no_puede_modificar_pasajeros(
    cliente,
    monkeypatch,
    metodo,
    ruta,
    datos
):
    monkeypatch.setattr(
        passenger_service,
        "crear_pasajero",
        AsyncMock(return_value=201)
    )
    monkeypatch.setattr(
        passenger_service,
        "actualizar_pasajero",
        AsyncMock(return_value=101)
    )
    monkeypatch.setattr(
        passenger_service,
        "eliminar_pasajero",
        AsyncMock(return_value=101)
    )
    monkeypatch.setattr(
        passenger_service,
        "asignar_pasajero",
        AsyncMock(return_value=True)
    )
    monkeypatch.setattr(
        passenger_service,
        "desvincular_pasajero",
        AsyncMock(return_value=True)
    )

    if datos is not None:
        respuesta = getattr(cliente, metodo)(ruta, json=datos)
    else:
        respuesta = getattr(cliente, metodo)(ruta)

    assert respuesta.status_code == 403


@pytest.mark.parametrize(
    "cliente",
    ["Operador"],
    indirect=True
)
def test_operador_puede_crear_pasajeros(cliente, monkeypatch):
    crear = AsyncMock(return_value=201)

    monkeypatch.setattr(
        passenger_service,
        "crear_pasajero",
        crear
    )

    respuesta = cliente.post(
        "/api/v1/passengers/",
        json={
            "name": "Carlos Ruiz",
            "code": "PAS-003",
            "phone": "3009999999",
            "custom_fields": {}
        }
    )

    assert respuesta.status_code == 201
    crear.assert_awaited_once()


@pytest.mark.parametrize(
    "cliente",
    ["Operador"],
    indirect=True
)
@pytest.mark.parametrize(
    "metodo, ruta, datos, servicio, resultado",
    [
        (
            "put",
            "/api/v1/passengers/101",
            {
                "name": "Juan Pérez actualizado",
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
    ],
    ids=[
        "actualizar",
        "eliminar",
        "asignar",
        "desvincular"
    ]
)
def test_operador_puede_modificar_pasajeros(
    cliente,
    monkeypatch,
    metodo,
    ruta,
    datos,
    servicio,
    resultado
):
    operacion = AsyncMock(return_value=resultado)

    monkeypatch.setattr(
        passenger_service,
        servicio,
        operacion
    )

    if datos is not None:
        respuesta = getattr(cliente, metodo)(ruta, json=datos)
    else:
        respuesta = getattr(cliente, metodo)(ruta)

    assert respuesta.status_code == 200
    operacion.assert_awaited_once()


@pytest.mark.parametrize(
    "metodo, ruta, datos",
    [
        ("get", "/api/v1/passengers/", None),
        (
            "post",
            "/api/v1/passengers/",
            {
                "name": "Carlos Ruiz",
                "code": "PAS-003",
                "phone": "3009999999",
                "custom_fields": {}
            }
        ),
        (
            "put",
            "/api/v1/passengers/101",
            {
                "name": "Juan Pérez actualizado",
                "code": "PAS-001",
                "phone": "3001234567",
                "custom_fields": {}
            }
        ),
        ("delete", "/api/v1/passengers/101", None),
        ("post", "/api/v1/passengers/101/asignar/12345", None),
        ("delete", "/api/v1/passengers/101/desvincular/12345", None)
    ],
    ids=[
        "consultar",
        "crear",
        "actualizar",
        "eliminar",
        "asignar",
        "desvincular"
    ]
)
def test_usuario_sin_autenticacion_no_puede_acceder(
    metodo,
    ruta,
    datos
):
    app.dependency_overrides.clear()

    token = generar_csrf_token()
    origen = next(iter(ALLOWED_ORIGINS))

    with TestClient(app) as test_client:
        test_client.cookies.set("csrf_token", token)

        test_client.headers.update({
            "Origin": origen,
            "X-CSRF-Token": token
        })

        if datos is not None:
            respuesta = getattr(test_client, metodo)(ruta, json=datos)
        else:
            respuesta = getattr(test_client, metodo)(ruta)

    assert respuesta.status_code == 401
