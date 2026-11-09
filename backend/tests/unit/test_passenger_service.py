
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
            campos_personalizados={
                "Área": "Sur",
                "_telefono": "3001111111"
            },
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
                "jp": {
                    "Área": "Norte",
                    "Turno": "Mañana",
                    "_telefono": "3001234567"
                },
                "bu": 0,
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
            "Turno": "Mañana",
            "_telefono": "3001234567"
        }

        assert llamada["telefono"] == "3001234567"

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

@pytest.mark.parametrize("datos", [None, [], "incorrecto", 123])
def test_obtener_pasajeros_rechaza_tags_invalidos(datos):
    async def ejecutar():
        servicio, cliente = crear_servicio()
        cliente.get_resources.return_value = [
            {"id": RESOURCE_ID, "tags": datos}
        ]

        with pytest.raises(RuntimeError, match="estructura inesperada"):
            await servicio.obtener_pasajeros()

    asyncio.run(ejecutar())


def test_crear_pasajero_rechaza_telefono_duplicado():
    async def ejecutar():
        servicio, cliente = crear_servicio()
        configurar_pasajeros(cliente, [
            {
                "id": 101,
                "n": "Juan",
                "c": "PAS-001",
                "p": "3001234567",
                "bu": 0,
                "jp": {}
            }
        ])

        with pytest.raises(ValueError, match="teléfono"):
            await servicio.crear_pasajero(
                nombre="Ana",
                telefono="3001234567"
            )

        cliente.actualizar_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


@pytest.mark.parametrize(
    "campos",
    [
        ["incorrecto"],
        {"": "valor"},
        {"Área": 123},
        {"_telefono": "3001234567"}
    ]
)
def test_crear_pasajero_rechaza_campos_personalizados_invalidos(campos):
    async def ejecutar():
        servicio, cliente = crear_servicio()

        with pytest.raises(ValueError):
            await servicio.crear_pasajero(
                nombre="Ana",
                campos_personalizados=campos
            )

        cliente.actualizar_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


def test_crear_pasajero_rechaza_respuesta_invalida():
    async def ejecutar():
        servicio, cliente = crear_servicio()
        configurar_pasajeros(cliente, [])
        cliente.actualizar_pasajero.return_value = {"id": 201}

        with pytest.raises(RuntimeError, match="respuesta inesperada"):
            await servicio.crear_pasajero("Ana")

    asyncio.run(ejecutar())


def test_actualizar_pasajero_rechaza_id_invalido():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        with pytest.raises(ValueError, match="ID"):
            await servicio.actualizar_pasajero(0, "Ana")

        cliente.get_resources.assert_not_awaited()

    asyncio.run(ejecutar())


def test_actualizar_pasajero_rechaza_codigo_duplicado():
    async def ejecutar():
        servicio, cliente = crear_servicio()
        configurar_pasajeros(cliente, [
            {
                "id": 101, "n": "Juan", "c": "PAS-001",
                "bu": 0, "jp": {}
            },
            {
                "id": 102, "n": "Ana", "c": "PAS-002",
                "bu": 0, "jp": {}
            }
        ])

        with pytest.raises(ValueError, match="otro pasajero con ese código"):
            await servicio.actualizar_pasajero(
                101, "Juan", codigo="pas-002"
            )

        cliente.actualizar_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


def test_actualizar_pasajero_rechaza_telefono_duplicado():
    async def ejecutar():
        servicio, cliente = crear_servicio()
        configurar_pasajeros(cliente, [
            {
                "id": 101, "n": "Juan", "p": "3001111111",
                "bu": 0, "jp": {}
            },
            {
                "id": 102, "n": "Ana", "p": "3002222222",
                "bu": 0, "jp": {}
            }
        ])

        with pytest.raises(ValueError, match="otro pasajero con ese teléfono"):
            await servicio.actualizar_pasajero(
                101, "Juan", telefono="3002222222"
            )

        cliente.actualizar_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


def test_actualizar_pasajero_rechaza_respuesta_invalida():
    async def ejecutar():
        servicio, cliente = crear_servicio()
        configurar_pasajeros(cliente, [
            {"id": 101, "n": "Juan", "bu": 0, "jp": {}}
        ])
        cliente.actualizar_pasajero.return_value = [102, {}]

        with pytest.raises(RuntimeError, match="respuesta inesperada"):
            await servicio.actualizar_pasajero(101, "Juan")

    asyncio.run(ejecutar())


def test_actualizar_pasajero_rechaza_campos_personalizados_invalidos():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        with pytest.raises(ValueError, match="diccionario"):
            await servicio.actualizar_pasajero(
                101, "Juan", campos_personalizados=["incorrecto"]
            )

        cliente.get_resources.assert_not_awaited()

    asyncio.run(ejecutar())


def test_eliminar_pasajero_rechaza_id_invalido():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        with pytest.raises(ValueError, match="ID"):
            await servicio.eliminar_pasajero(0)

        cliente.get_resources.assert_not_awaited()

    asyncio.run(ejecutar())


def test_eliminar_pasajero_rechaza_respuesta_invalida():
    async def ejecutar():
        servicio, cliente = crear_servicio()
        configurar_pasajeros(cliente, [
            {"id": 101, "n": "Juan", "bu": 0, "jp": {}}
        ])
        cliente.actualizar_pasajero.return_value = [101, {}]

        with pytest.raises(RuntimeError, match="respuesta inesperada"):
            await servicio.eliminar_pasajero(101)

    asyncio.run(ejecutar())


@pytest.mark.parametrize(
    "passenger_id,unit_id",
    [(0, 100), (100, 0), (-1, 100), (100, -1)]
)
def test_asignar_pasajero_rechaza_ids_invalidos(
    passenger_id, unit_id
):
    async def ejecutar():
        servicio, cliente = crear_servicio()

        with pytest.raises(ValueError, match="ID"):
            await servicio.asignar_pasajero(passenger_id, unit_id)

        cliente.get_resources.assert_not_awaited()
        cliente.vincular_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


def test_desvincular_pasajero_inexistente():
    async def ejecutar():
        servicio, cliente = crear_servicio()
        configurar_pasajeros(cliente, [])

        with pytest.raises(ValueError, match="no existe"):
            await servicio.desvincular_pasajero(999, 100)

        cliente.vincular_pasajero.assert_not_awaited()

    asyncio.run(ejecutar())


def test_desvincular_pasajero_rechaza_ids_invalidos():
    async def ejecutar():
        servicio, cliente = crear_servicio()

        with pytest.raises(ValueError, match="ID"):
            await servicio.desvincular_pasajero(0, 100)

        cliente.get_resources.assert_not_awaited()

    asyncio.run(ejecutar())