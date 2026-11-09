import asyncio
import json

import httpx
import pytest

from app.integrations.wialon_client import WialonClient


def crear_cliente(monkeypatch, handler):
    monkeypatch.setenv("WIALON_API_URL", "https://wialon.test/wialon/ajax.html")
    monkeypatch.setenv("WIALON_TOKEN", "token-prueba")
    cliente = WialonClient()
    cliente._http_client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    )
    return cliente


def test_login_guarda_identificador_de_sesion(monkeypatch):
    async def ejecutar():
        solicitudes = []

        def handler(request):
            solicitudes.append(request)
            return httpx.Response(200, json={"eid": "sesion-123"})

        cliente = crear_cliente(monkeypatch, handler)

        try:
            assert await cliente.login() is True
            assert await cliente.login() is True
            assert cliente.session_id == "sesion-123"
            assert len(solicitudes) == 1
            assert solicitudes[0].url.params["svc"] == "token/login"
            assert json.loads(solicitudes[0].url.params["params"]) == {
                "token": "token-prueba"
            }
        finally:
            await cliente.cerrar()

    asyncio.run(ejecutar())


def test_login_rechaza_respuesta_sin_eid(monkeypatch):
    async def ejecutar():
        cliente = crear_cliente(
            monkeypatch,
            lambda request: httpx.Response(200, json={"error": 7})
        )

        try:
            with pytest.raises(RuntimeError, match="identificador de sesión"):
                await cliente.login()
        finally:
            await cliente.cerrar()

    asyncio.run(ejecutar())


def test_get_units_consulta_y_devuelve_items(monkeypatch):
    async def ejecutar():
        servicios = []

        def handler(request):
            servicio = request.url.params["svc"]
            servicios.append(servicio)

            if servicio == "token/login":
                return httpx.Response(200, json={"eid": "sesion-123"})

            return httpx.Response(
                200,
                json={"items": [{"id": 10, "nm": "Vehículo de prueba"}]}
            )

        cliente = crear_cliente(monkeypatch, handler)

        try:
            resultado = await cliente.get_units()
            assert resultado == [{"id": 10, "nm": "Vehículo de prueba"}]
            assert servicios == ["token/login", "core/search_items"]
        finally:
            await cliente.cerrar()

    asyncio.run(ejecutar())


def test_consultar_renueva_sesion_y_reintenta(monkeypatch):
    async def ejecutar():
        sesiones = iter(["sesion-inicial", "sesion-renovada"])
        solicitudes = []
        consultas = 0

        def handler(request):
            nonlocal consultas
            servicio = request.url.params["svc"]
            solicitudes.append((servicio, request.url.params.get("sid")))

            if servicio == "token/login":
                return httpx.Response(200, json={"eid": next(sesiones)})

            consultas += 1
            if consultas == 1:
                return httpx.Response(200, json={"error": 1})

            return httpx.Response(200, json={"items": [{"id": 20}]})

        cliente = crear_cliente(monkeypatch, handler)

        try:
            resultado = await cliente.get_units()
            assert resultado == [{"id": 20}]
            assert cliente.session_id == "sesion-renovada"
            assert solicitudes == [
                ("token/login", None),
                ("core/search_items", "sesion-inicial"),
                ("token/login", None),
                ("core/search_items", "sesion-renovada")
            ]
        finally:
            await cliente.cerrar()

    asyncio.run(ejecutar())


def test_consultar_falla_si_wialon_devuelve_error_persistente(monkeypatch):
    async def ejecutar():
        def handler(request):
            if request.url.params["svc"] == "token/login":
                return httpx.Response(200, json={"eid": "sesion-123"})
            return httpx.Response(200, json={"error": 2})

        cliente = crear_cliente(monkeypatch, handler)

        try:
            with pytest.raises(RuntimeError, match="código 2"):
                await cliente.get_units()
        finally:
            await cliente.cerrar()

    asyncio.run(ejecutar())


def test_metodos_rechazan_identificadores_e_intervalos_invalidos(monkeypatch):
    async def ejecutar():
        cliente = crear_cliente(
            monkeypatch,
            lambda request: httpx.Response(200, json={"eid": "sesion-123"})
        )

        try:
            with pytest.raises(ValueError, match="vehículo"):
                await cliente.get_unit_drivers(0)

            with pytest.raises(ValueError, match="recurso"):
                await cliente.get_driver_bindings(0, 100, 200)

            with pytest.raises(ValueError, match="intervalo"):
                await cliente.get_driver_bindings(1, 200, 100)

            with pytest.raises(ValueError, match="vehículo"):
                await cliente.bind_unit_driver(1, 0, 10)

            with pytest.raises(ValueError, match="conductor"):
                await cliente.bind_unit_driver(1, 10, 0)
        finally:
            await cliente.cerrar()

    asyncio.run(ejecutar())

@pytest.mark.parametrize(
    "accion, campo_id, nombre, valor",
    [
        ("create", 0, "PLACA", "ABC123"),
        ("update", 12, "PLACA", "XYZ789"),
        ("delete", 12, "", "")
    ]
)
def test_gestionar_campo_personalizado_envia_parametros(
    monkeypatch, accion, campo_id, nombre, valor
):
    async def ejecutar():
        solicitudes = []

        def handler(request):
            servicio = request.url.params["svc"]

            if servicio == "token/login":
                return httpx.Response(200, json={"eid": "sesion-123"})

            solicitudes.append(
                json.loads(request.url.params["params"])
            )
            return httpx.Response(200, json={"error": 0})

        cliente = crear_cliente(monkeypatch, handler)

        try:
            resultado = await cliente.gestionar_campo_personalizado(
                unidad_id=957,
                campo_id=campo_id,
                accion=accion,
                nombre=nombre,
                valor=valor
            )

            assert resultado == {"error": 0}
            assert solicitudes == [{
                "itemId": 957,
                "id": campo_id,
                "callMode": accion,
                **({"n": nombre, "v": valor} if accion != "delete" else {})
            }]
        finally:
            await cliente.cerrar()

    asyncio.run(ejecutar())