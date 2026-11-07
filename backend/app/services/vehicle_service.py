
import asyncio
import time

from app.integrations.wialon_client import WialonClient
from app.integrations.wialon_mapper import convertir_vehiculo
from app.domain.vehicle import Vehicle


class VehicleService:

    def __init__(self):
        self.wialon_client = WialonClient()
        self._cache_vehiculos = None
        self._cache_timestamp = 0
        self._cache_ttl = 15
        self._cache_lock = asyncio.Lock()

    async def obtener_vehiculos(self) -> list[Vehicle]:

        async with self._cache_lock:

            ahora = time.monotonic()

            if (
                self._cache_vehiculos is not None
                and ahora - self._cache_timestamp < self._cache_ttl
            ):
                return self._cache_vehiculos

            datos_vehiculos = await self.wialon_client.get_units()

            vehiculos = [
                convertir_vehiculo(datos)
                for datos in datos_vehiculos
            ]

            self._cache_vehiculos = vehiculos
            self._cache_timestamp = time.monotonic()

            return vehiculos


vehicle_service = VehicleService()
