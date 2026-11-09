import asyncio

import pytest

from app.services.driver_service import DriverService


class WialonClientFake:
    def __init__(self, conductores=None, unidades=None):
        self.conductores = conductores or {}
        self.unidades = unidades or []
        self.operaciones = []

    async def get_resources(self):
        return [{"id": 123, "drvrs": self.conductores}]

    async def get_units(self):
        return self.unidades

    async def bind_unit_driver(self, **kwargs):
        self.operaciones.append(("asignar", kwargs))
        return True

    async def crear_conductor(self, **kwargs):
        self.operaciones.append(("crear", kwargs))
        return [50, {}]

    async def actualizar_conductor(self, **kwargs):
        self.operaciones.append(("actualizar", kwargs))
        return [kwargs["driver_id"], {}]

    async def eliminar_conductor(self, **kwargs):
        self.operaciones.append(("eliminar", kwargs))
        return [kwargs["driver_id"], None]


def crear_servicio(monkeypatch, conductores=None, unidades=None):
    monkeypatch.setenv("WIALON_RESOURCE_ID", "123")
    cliente = WialonClientFake(conductores, unidades)
    return DriverService(cliente), cliente


def ejecutar(coroutine):
    return asyncio.run(coroutine)


def test_obtener_conductores_correctamente(monkeypatch):
    servicio, _ = crear_servicio(
        monkeypatch,
        {
            "1": {
                "id": 1,
                "n": "Carlos",
                "c": "COD01",
                "p": "3001234567",
                "bu": 100,
                "jp": {"licencia": "ABC123"}
            }
        }
    )

    conductores = ejecutar(servicio.obtener_conductores())

    assert len(conductores) == 1
    assert conductores[0].id == 1
    assert conductores[0].name == "Carlos"
    assert conductores[0].assigned_unit_id == 100
    assert conductores[0].custom_fields == {"licencia": "ABC123"}


def test_obtener_conductores_recurso_inexistente(monkeypatch):
    servicio, cliente = crear_servicio(monkeypatch)
    cliente.get_resources = lambda: None

    async def recursos():
        return [{"id": 999, "drvrs": {}}]

    cliente.get_resources = recursos

    with pytest.raises(RuntimeError, match="No se encontró el recurso"):
        ejecutar(servicio.obtener_conductores())


def test_obtener_asignaciones_correctamente(monkeypatch):
    servicio, _ = crear_servicio(
        monkeypatch,
        {
            "1": {"id": 1, "n": "Carlos", "bu": 100},
            "2": {"id": 2, "n": "Ana", "bu": 0},
            "3": {"id": 3, "n": "Luis", "bu": 200}
        }
    )

    resultado = ejecutar(servicio.obtener_asignaciones())

    assert resultado["total"] == 2
    assert resultado["completa"] is True
    assert resultado["vehiculos_con_error"] == 0
    assert {item["unit_id"] for item in resultado["resultados"]} == {
        100, 200
    }


def test_asignar_conductor_correctamente(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos"}},
        [{"id": 100}]
    )

    resultado = ejecutar(servicio.asignar_conductor(1, 100))

    assert resultado is True
    assert cliente.operaciones[0][0] == "asignar"
    assert cliente.operaciones[0][1]["driver_id"] == 1
    assert cliente.operaciones[0][1]["unit_id"] == 100
    assert cliente.operaciones[0][1]["asignar"] is True


@pytest.mark.parametrize(
    "driver_id,unit_id",
    [(0, 100), (1, 0), (-1, 100), (1, -100)]
)
def test_asignar_conductor_rechaza_ids_invalidos(
    monkeypatch, driver_id, unit_id
):
    servicio, _ = crear_servicio(monkeypatch)

    with pytest.raises(ValueError, match="ID"):
        ejecutar(servicio.asignar_conductor(driver_id, unit_id))


def test_asignar_conductor_inexistente(monkeypatch):
    servicio, _ = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos"}},
        [{"id": 100}]
    )

    with pytest.raises(ValueError, match="no existe en el recurso"):
        ejecutar(servicio.asignar_conductor(2, 100))


def test_asignar_vehiculo_inexistente(monkeypatch):
    servicio, _ = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos"}},
        [{"id": 200}]
    )

    with pytest.raises(ValueError, match="vehículo no existe"):
        ejecutar(servicio.asignar_conductor(1, 100))


def test_no_asignar_conductor_ya_asignado(monkeypatch):
    servicio, _ = crear_servicio(
        monkeypatch,
        {
            "1": {"id": 1, "n": "Carlos", "bu": 200},
            "2": {"id": 2, "n": "Ana"}
        },
        [{"id": 100}, {"id": 200}]
    )

    with pytest.raises(ValueError, match="ya está asignado"):
        ejecutar(servicio.asignar_conductor(1, 100))


def test_no_asignar_vehiculo_ocupado(monkeypatch):
    servicio, _ = crear_servicio(
        monkeypatch,
        {
            "1": {"id": 1, "n": "Carlos"},
            "2": {"id": 2, "n": "Ana", "bu": 100}
        },
        [{"id": 100}, {"id": 200}]
    )

    with pytest.raises(ValueError, match="ya tiene un conductor"):
        ejecutar(servicio.asignar_conductor(1, 100))


def test_desvincular_conductor_correctamente(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos", "bu": 100}}
    )

    resultado = ejecutar(servicio.desvincular_conductor(1, 100))

    assert resultado is True
    assert cliente.operaciones[0][0] == "asignar"
    assert cliente.operaciones[0][1]["asignar"] is False


def test_desvincular_conductor_no_asignado(monkeypatch):
    servicio, _ = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos", "bu": 200}}
    )

    with pytest.raises(ValueError, match="no está asignado"):
        ejecutar(servicio.desvincular_conductor(1, 100))


def test_crear_conductor_correctamente(monkeypatch):
    servicio, cliente = crear_servicio(monkeypatch)

    resultado = ejecutar(
        servicio.crear_conductor(
            nombre=" Carlos ",
            codigo=" COD01 ",
            telefono=" 3001234567 "
        )
    )

    assert resultado == 50
    assert cliente.operaciones[0][0] == "crear"
    assert cliente.operaciones[0][1]["nombre"] == " Carlos "
    assert cliente.operaciones[0][1]["codigo"] == "COD01"
    assert cliente.operaciones[0][1]["telefono"] == "3001234567"


def test_crear_conductor_codigo_duplicado(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos", "c": "COD01"}}
    )

    with pytest.raises(ValueError, match="código"):
        ejecutar(
            servicio.crear_conductor(
                nombre="Ana",
                codigo="cod01"
            )
        )

    assert cliente.operaciones == []


def test_crear_conductor_telefono_duplicado(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos", "p": "3001234567"}}
    )

    with pytest.raises(ValueError, match="teléfono"):
        ejecutar(
            servicio.crear_conductor(
                nombre="Ana",
                telefono="3001234567"
            )
        )

    assert cliente.operaciones == []


def test_crear_conductor_rechaza_respuesta_invalida(monkeypatch):
    servicio, cliente = crear_servicio(monkeypatch)

    async def crear(**kwargs):
        return {"id": 50}

    cliente.crear_conductor = crear

    with pytest.raises(RuntimeError, match="respuesta inesperada"):
        ejecutar(servicio.crear_conductor("Carlos"))


def test_actualizar_conductor_correctamente(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {
            "1": {
                "id": 1,
                "n": "Carlos",
                "c": "COD01",
                "p": "3001234567",
                "jp": {"licencia": "ABC123"}
            }
        }
    )

    resultado = ejecutar(
        servicio.actualizar_conductor(
            1,
            "Carlos actualizado",
            "COD02",
            "3007654321"
        )
    )

    assert resultado == 1
    assert cliente.operaciones[0][0] == "actualizar"
    assert cliente.operaciones[0][1]["campos_personalizados"] == {
        "licencia": "ABC123"
    }


def test_actualizar_conductor_inexistente(monkeypatch):
    servicio, cliente = crear_servicio(monkeypatch)

    with pytest.raises(ValueError, match="No se encontró"):
        ejecutar(servicio.actualizar_conductor(1, "Carlos"))

    assert cliente.operaciones == []


def test_actualizar_conductor_codigo_duplicado(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {
            "1": {"id": 1, "n": "Carlos"},
            "2": {"id": 2, "n": "Ana", "c": "COD02"}
        }
    )

    with pytest.raises(ValueError, match="otro conductor con ese código"):
        ejecutar(
            servicio.actualizar_conductor(1, "Carlos", codigo="cod02")
        )

    assert cliente.operaciones == []


def test_actualizar_conductor_telefono_duplicado(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {
            "1": {"id": 1, "n": "Carlos"},
            "2": {"id": 2, "n": "Ana", "p": "3001234567"}
        }
    )

    with pytest.raises(ValueError, match="otro conductor con ese teléfono"):
        ejecutar(
            servicio.actualizar_conductor(
                1, "Carlos", telefono="3001234567"
            )
        )

    assert cliente.operaciones == []


def test_actualizar_conductor_rechaza_respuesta_invalida(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos"}}
    )

    async def actualizar(**kwargs):
        return [2, {}]

    cliente.actualizar_conductor = actualizar

    with pytest.raises(RuntimeError, match="respuesta inesperada"):
        ejecutar(servicio.actualizar_conductor(1, "Carlos"))


def test_eliminar_conductor_correctamente(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos"}}
    )

    resultado = ejecutar(servicio.eliminar_conductor(1))

    assert resultado == 1
    assert cliente.operaciones[0][0] == "eliminar"


def test_no_eliminar_conductor_asignado(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos", "bu": 100}}
    )

    with pytest.raises(ValueError, match="conductor asignado"):
        ejecutar(servicio.eliminar_conductor(1))

    assert cliente.operaciones == []


def test_eliminar_conductor_inexistente(monkeypatch):
    servicio, cliente = crear_servicio(monkeypatch)

    with pytest.raises(ValueError, match="No se encontró"):
        ejecutar(servicio.eliminar_conductor(1))

    assert cliente.operaciones == []


def test_eliminar_conductor_rechaza_respuesta_invalida(monkeypatch):
    servicio, cliente = crear_servicio(
        monkeypatch,
        {"1": {"id": 1, "n": "Carlos"}}
    )

    async def eliminar(**kwargs):
        return [1, {}]

    cliente.eliminar_conductor = eliminar

    with pytest.raises(RuntimeError, match="respuesta inesperada"):
        ejecutar(servicio.eliminar_conductor(1))