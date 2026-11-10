import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.services.trip_service import TripService
from app.services.vehicle_service import vehicle_service


def test_obtener_historial_transforma_viaje_wialon():
    async def ejecutar():
        cliente = SimpleNamespace(
            get_unit_trips=AsyncMock(return_value={
                "trips": [{
                    "from": {
                        "t": 1000,
                        "i": 0,
                        "p": {"y": 4.6, "x": -74.1}
                    },
                    "to": {
                        "t": 1600,
                        "i": 1,
                        "p": {"y": 4.7, "x": -74.2}
                    },
                    "m": 5000
                }],
                "messages": [
                    {"t": 1000, "pos": {"y": 4.6, "x": -74.1, "s": 10}},
                    {"t": 1600, "pos": {"y": 4.7, "x": -74.2, "s": 30}}
                ],
                "message_count": 2
            })
        )
        servicio = TripService(wialon_client=cliente)
        vehiculo = SimpleNamespace(id=957, name="Vehículo prueba")

        with patch.object(
            vehicle_service,
            "obtener_vehiculos",
            new=AsyncMock(return_value=[vehiculo])
        ):
            resultado = await servicio.obtener_historial(
                957,
                datetime.fromtimestamp(900, tz=timezone.utc),
                datetime.fromtimestamp(1700, tz=timezone.utc)
            )

        assert resultado["vehicle_id"] == 957
        assert resultado["vehicle_name"] == "Vehículo prueba"
        assert resultado["total_viajes"] == 1
        assert resultado["simulated"] is False

        viaje = resultado["viajes"][0]
        assert viaje["duration_seconds"] == 600
        assert viaje["distance_km"] == 5.0
        assert viaje["average_speed"] == 30.0
        assert viaje["max_speed"] == 30.0
        assert viaje["simulated"] is False
        assert viaje["route_points"] == [
            {
                "elapsed_seconds": 0,
                "latitude": 4.6,
                "longitude": -74.1,
                "speed": 10.0
            },
            {
                "elapsed_seconds": 600,
                "latitude": 4.7,
                "longitude": -74.2,
                "speed": 30.0
            }
        ]
        cliente.get_unit_trips.assert_awaited_once_with(
            957, 900, 1700
        )

    asyncio.run(ejecutar())


def test_obtener_historial_ignora_viaje_sin_datos_validos():
    async def ejecutar():
        cliente = SimpleNamespace(
            get_unit_trips=AsyncMock(return_value={
                "trips": [
                    {"from": {"t": "no-fecha"}, "to": {"t": 1600}, "m": 1000},
                    {
                        "from": {"t": 1000, "i": 0},
                        "to": {"t": 1600, "i": 1},
                        "m": 1000
                    }
                ],
                "messages": [
                    {"t": "timestamp-invalido", "pos": {"y": 4.6, "x": -74.1}},
                    {"t": 1200, "pos": {"y": 4.65, "x": -74.15, "s": 12}},
                    {"t": 1600, "pos": {"y": 4.7, "x": -74.2, "s": 18}}
                ],
                "message_count": 3
            })
        )
        servicio = TripService(wialon_client=cliente)
        vehiculo = SimpleNamespace(id=957, name="Vehículo prueba")

        with patch.object(
            vehicle_service,
            "obtener_vehiculos",
            new=AsyncMock(return_value=[vehiculo])
        ):
            resultado = await servicio.obtener_historial(
                957,
                datetime.fromtimestamp(900, tz=timezone.utc),
                datetime.fromtimestamp(1700, tz=timezone.utc)
            )

        assert resultado["total_viajes"] == 1
        assert len(resultado["viajes"][0]["route_points"]) == 2

    asyncio.run(ejecutar())


def test_obtener_historial_rechaza_fechas_invertidas():
    async def ejecutar():
        cliente = SimpleNamespace(get_unit_trips=AsyncMock())
        servicio = TripService(wialon_client=cliente)

        with patch.object(
            vehicle_service,
            "obtener_vehiculos",
            new=AsyncMock()
        ):
            try:
                await servicio.obtener_historial(
                    957,
                    datetime(2026, 1, 2),
                    datetime(2026, 1, 1)
                )
            except ValueError as error:
                assert "fecha inicial" in str(error)
            else:
                raise AssertionError("Se esperaba ValueError")

        cliente.get_unit_trips.assert_not_awaited()

    asyncio.run(ejecutar())
