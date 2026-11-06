
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

            # 1. Comprobar si existe una caché vigente.
            if (
                self._cache_vehiculos is not None
                and ahora - self._cache_timestamp < self._cache_ttl
            ):
                return self._cache_vehiculos
                

            # 2. Consultar Wialon.
            datos_vehiculos = await self.wialon_client.get_units()

            # 3. Transformar los datos.
            vehiculos = [
                convertir_vehiculo(datos)
                for datos in datos_vehiculos
            ]

            # 4. Guardar resultados en caché.
            self._cache_vehiculos = vehiculos
            self._cache_timestamp = time.monotonic()

            return vehiculos


# Instancia compartida para toda la aplicación.
vehicle_service = VehicleService()
