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

    async def invalidar_cache(self):

        async with self._cache_lock:
            self._cache_vehiculos = None
            self._cache_timestamp = 0

    async def actualizar_campo_personalizado(
        self,
        unidad_id: int,
        campo_id: int,
        nombre: str,
        valor: str
    ):

        vehiculos = await self.obtener_vehiculos()

        vehiculo = next(
            (v for v in vehiculos if v.id == unidad_id),
            None
        )

        if vehiculo is None:
            raise ValueError("El vehículo no existe")

        if str(campo_id) not in vehiculo.custom_fields:
            raise ValueError("El campo personalizado no existe")

        resultado = await self.wialon_client.gestionar_campo_personalizado(
            unidad_id=unidad_id,
            campo_id=campo_id,
            accion="update",
            nombre=nombre,
            valor=valor
        )

        await self.invalidar_cache()

        return resultado


vehicle_service = VehicleService()