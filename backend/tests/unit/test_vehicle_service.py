
import asyncio
from unittest.mock import AsyncMock, patch

from app.services.vehicle_service import VehicleService


def test_obtener_vehiculos_correctamente():
    async def ejecutar():
        servicio = VehicleService()

        servicio.wialon_client.get_units = AsyncMock(
            return_value=[
                {
                    "id": 1,
                    "nm": "Vehículo de prueba"
                }
            ]
        )

        with patch(
            "app.services.vehicle_service.convertir_vehiculo"
        ) as mapper:
            vehiculo_mock = object()
            mapper.return_value = vehiculo_mock

            resultado = await servicio.obtener_vehiculos()

            assert resultado == [vehiculo_mock]
            servicio.wialon_client.get_units.assert_awaited_once()
            mapper.assert_called_once()

    asyncio.run(ejecutar())


def test_obtener_vehiculos_utiliza_cache():
    async def ejecutar():
        servicio = VehicleService()

        servicio.wialon_client.get_units = AsyncMock(
            return_value=[]
        )

        primera_consulta = await servicio.obtener_vehiculos()
        segunda_consulta = await servicio.obtener_vehiculos()

        assert primera_consulta is segunda_consulta
        servicio.wialon_client.get_units.assert_awaited_once()

    asyncio.run(ejecutar())


def test_obtener_vehiculos_actualiza_cache():
    async def ejecutar():
        servicio = VehicleService()

        servicio.wialon_client.get_units = AsyncMock(
            return_value=[]
        )

        with patch(
            "app.services.vehicle_service.time.monotonic",
            side_effect=[100, 100, 116, 116]
        ):
            await servicio.obtener_vehiculos()
            await servicio.obtener_vehiculos()

        assert servicio.wialon_client.get_units.await_count == 2

    asyncio.run(ejecutar())


def test_obtener_vehiculos_propagacion_error_wialon():
    async def ejecutar():
        servicio = VehicleService()

        servicio.wialon_client.get_units = AsyncMock(
            side_effect=RuntimeError("Error de conexión")
        )

        try:
            await servicio.obtener_vehiculos()
            assert False, "Se esperaba RuntimeError"
        except RuntimeError as error:
            assert str(error) == "Error de conexión"

    asyncio.run(ejecutar())
