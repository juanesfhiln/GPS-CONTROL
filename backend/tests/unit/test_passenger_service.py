
import asyncio
from unittest.mock import AsyncMock

import pytest

from app.domain.passenger import Passenger
from app.services.passenger_service import PassengerService


RESOURCE_ID = 27668776


def crear_servicio():
    cliente = AsyncMock()

    servicio = PassengerService(cliente)

    return servicio, cliente


def configurar_pasajeros(cliente, pasajeros):
    cliente.get_resources.return_value = [
        {
            "id": RESOURCE_ID,
            "tags": {
                str(p["id"]): p
                for p in pasajeros
            }
        }
    ]

def test_obtener_pasajeros_correctamente():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "3001234567",
                "bu": 0,
                "jp": {"Área": "Norte"}
            }
        ])

        pasajeros = await servicio.obtener_pasajeros()

        assert len(pasajeros) == 1
        assert pasajeros[0].id == 101
        assert pasajeros[0].name == "Juan Pérez"
        assert pasajeros[0].custom_fields == {"Área": "Norte"}

        cliente.get_resources.assert_awaited_once()

    asyncio.run(ejecutar())


def test_obtener_pasajeros_recurso_inexistente():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        cliente.get_resources.return_value = []

        with pytest.raises(RuntimeError):
            await servicio.obtener_pasajeros()

    asyncio.run(ejecutar())

def test_crear_pasajero_correctamente():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [])

        cliente.actualizar_pasajero.return_value = [
            201,
            {"id": 201, "n": "Ana Gómez"}
        ]

        resultado = await servicio.crear_pasajero(
            nombre="Ana Gómez",
            codigo="PAS-002",
            telefono="3001111111",
            campos_personalizados={"Área": "Sur"}
        )

        assert resultado == 201

        cliente.actualizar_pasajero.assert_awaited_once_with(
            resource_id=RESOURCE_ID,
            tag_id=0,
            nombre="Ana Gómez",
            codigo="PAS-002",
            telefono="3001111111",
            campos_personalizados={"Área": "Sur"},
            call_mode="create"
        )

    asyncio.run(ejecutar())


def test_crear_pasajero_nombre_vacio():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        with pytest.raises(ValueError):
            await servicio.crear_pasajero(nombre="   ")

        cliente.actualizar_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


def test_crear_pasajero_codigo_duplicado():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "",
                "bu": 0,
                "jp": {}
            }
        ])

        with pytest.raises(ValueError, match="código"):
            await servicio.crear_pasajero(
                nombre="Ana Gómez",
                codigo="pas-001"
            )

        cliente.actualizar_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


def test_actualizar_pasajero_conserva_campos_personalizados():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "3001234567",
                "bu": 0,
                "jp": {
                    "Área": "Norte",
                    "Turno": "Mañana"
                }
            }
        ])

        cliente.actualizar_pasajero.return_value = [
            101,
            {"id": 101}
        ]

        resultado = await servicio.actualizar_pasajero(
            passenger_id=101,
            nombre="Juan Pérez actualizado"
        )

        assert resultado == 101

        llamada = cliente.actualizar_pasajero.await_args.kwargs

        assert llamada["campos_personalizados"] == {
            "Área": "Norte",
            "Turno": "Mañana"
        }

    asyncio.run(ejecutar())


def test_actualizar_pasajero_permite_eliminar_campos_personalizados():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "",
                "bu": 0,
                "jp": {"Área": "Norte"}
            }
        ])

        cliente.actualizar_pasajero.return_value = [
            101,
            {"id": 101}
        ]

        await servicio.actualizar_pasajero(
            passenger_id=101,
            nombre="Juan Pérez",
            campos_personalizados={}
        )

        llamada = cliente.actualizar_pasajero.await_args.kwargs

        assert llamada["campos_personalizados"] == {}

    asyncio.run(ejecutar())

def test_no_eliminar_pasajero_asignado():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "",
                "bu": 12345,
                "jp": {}
            }
        ])

        with pytest.raises(ValueError, match="asignado"):
            await servicio.eliminar_pasajero(101)

        cliente.actualizar_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


def test_asignar_pasajero_correctamente():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "",
                "bu": 0,
                "jp": {}
            }
        ])

        cliente.get_units.return_value = [
            {"id": 12345}
        ]

        cliente.vincular_pasajero.return_value = {}

        resultado = await servicio.asignar_pasajero(101, 12345)

        assert resultado == {}

        cliente.vincular_pasajero.assert_awaited_once_with(
            resource_id=RESOURCE_ID,
            unit_id=12345,
            tag_id=101,
            asignar=True
        )

    asyncio.run(ejecutar())


def test_asignar_pasajero_inexistente():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [])

        with pytest.raises(ValueError, match="no existe"):
            await servicio.asignar_pasajero(999, 12345)

        cliente.vincular_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


def test_asignar_pasajero_vehiculo_inexistente():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "",
                "bu": 0,
                "jp": {}
            }
        ])

        cliente.get_units.return_value = []

        with pytest.raises(ValueError, match="vehículo"):
            await servicio.asignar_pasajero(101, 12345)

        cliente.vincular_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())

def test_asignar_pasajero_ya_asignado():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "",
                "bu": 12345,
                "jp": {}
            }
        ])

        cliente.get_units.return_value = [
            {"id": 12345}
        ]

        with pytest.raises(ValueError, match="ya está asignado"):
            await servicio.asignar_pasajero(101, 12345)

        cliente.get_units.assert_awaited_once()
        cliente.vincular_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())

def test_desvincular_pasajero_correctamente():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "",
                "bu": 12345,
                "jp": {}
            }
        ])

        cliente.vincular_pasajero.return_value = {}

        resultado = await servicio.desvincular_pasajero(101, 12345)

        assert resultado == {}

        cliente.vincular_pasajero.assert_awaited_once_with(
            resource_id=RESOURCE_ID,
            unit_id=12345,
            tag_id=101,
            asignar=False
        )

    asyncio.run(ejecutar())


def test_desvincular_pasajero_vehiculo_incorrecto():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "",
                "bu": 12345,
                "jp": {}
            }
        ])

        with pytest.raises(ValueError, match="no está asignado"):
            await servicio.desvincular_pasajero(101, 67890)

        cliente.vincular_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


def test_eliminar_pasajero_correctamente():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan Pérez",
                "c": "PAS-001",
                "p": "",
                "bu": 0,
                "jp": {}
            }
        ])

        cliente.actualizar_pasajero.return_value = [101, None]

        resultado = await servicio.eliminar_pasajero(101)

        assert resultado == 101

        cliente.actualizar_pasajero.assert_awaited_once_with(
            resource_id=RESOURCE_ID,
            tag_id=101,
            call_mode="delete"
        )

    asyncio.run(ejecutar())


def test_eliminar_pasajero_inexistente():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        configurar_pasajeros(cliente, [])

        with pytest.raises(ValueError, match="(?i)no se encontró"):
            await servicio.eliminar_pasajero(999)

        cliente.actualizar_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())
