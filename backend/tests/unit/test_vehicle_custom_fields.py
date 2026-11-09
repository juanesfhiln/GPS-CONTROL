import asyncio
from unittest.mock import AsyncMock, patch

import pytest
import time

from app.domain.vehicle import Vehicle
from app.services.vehicle_service import VehicleService


def crear_vehiculo():
    return Vehicle(
        id=957,
        name="957",
        latitude=4.6,
        longitude=-74.1,
        speed=0,
        heading=0,
        heading_cardinal="Norte",
        altitude=2600,
        position_time=None,
        last_message_time=None,
        status="detenido",
        custom_fields={
            "12": {
                "n": "PLACA",
                "v": "ABC123"
            }
        }
    )


def crear_servicio():
    with patch(
        "app.services.vehicle_service.WialonClient"
    ):
        servicio = VehicleService()

    servicio._cache_vehiculos = [crear_vehiculo()]
    servicio._cache_timestamp = time.monotonic()

    return servicio


def test_actualizar_campo_personalizado_correctamente():
    async def ejecutar():
        servicio = crear_servicio()

        servicio.wialon_client.gestionar_campo_personalizado = AsyncMock(
            return_value={"error": 0}
        )

        resultado = await servicio.actualizar_campo_personalizado(
            unidad_id=957,
            campo_id=12,
            nombre="PLACA",
            valor="XYZ789"
        )

        servicio.wialon_client.gestionar_campo_personalizado.assert_awaited_once_with(
            unidad_id=957,
            campo_id=12,
            accion="update",
            nombre="PLACA",
            valor="XYZ789"
        )

        assert resultado == {"error": 0}
        assert servicio._cache_vehiculos is None

    asyncio.run(ejecutar())


def test_rechazar_vehiculo_inexistente():
    async def ejecutar():
        servicio = crear_servicio()

        servicio.wialon_client.gestionar_campo_personalizado = AsyncMock()

        with pytest.raises(ValueError, match="El vehículo no existe"):
            await servicio.actualizar_campo_personalizado(
                unidad_id=999,
                campo_id=12,
                nombre="PLACA",
                valor="XYZ789"
            )

        servicio.wialon_client.gestionar_campo_personalizado.assert_not_awaited()

    asyncio.run(ejecutar())


def test_rechazar_campo_inexistente():
    async def ejecutar():
        servicio = crear_servicio()

        servicio.wialon_client.gestionar_campo_personalizado = AsyncMock()

        with pytest.raises(ValueError, match="El campo personalizado no existe"):
            await servicio.actualizar_campo_personalizado(
                unidad_id=957,
                campo_id=99,
                nombre="PLACA",
                valor="XYZ789"
            )

        servicio.wialon_client.gestionar_campo_personalizado.assert_not_awaited()

    asyncio.run(ejecutar())


def test_no_invalidar_cache_si_wialon_falla():
    async def ejecutar():
        servicio = crear_servicio()

        servicio.wialon_client.gestionar_campo_personalizado = AsyncMock(
            side_effect=RuntimeError("Error de Wialon")
        )

        with pytest.raises(RuntimeError):
            await servicio.actualizar_campo_personalizado(
                unidad_id=957,
                campo_id=12,
                nombre="PLACA",
                valor="XYZ789"
            )

        assert servicio._cache_vehiculos is not None

    asyncio.run(ejecutar())