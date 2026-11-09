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

            if not isinstance(datos_vehiculos, list):
                raise RuntimeError(
                    "Wialon devolvió una respuesta de vehículos inválida"
                )

            if not all(isinstance(datos, dict) for datos in datos_vehiculos):
                raise RuntimeError(
                    "Wialon devolvió datos de vehículos inválidos"
                )

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

    async def _obtener_vehiculo(self, unidad_id: int) -> Vehicle:
        if isinstance(unidad_id, bool) or not isinstance(unidad_id, int) or unidad_id <= 0:
            raise ValueError("El ID del vehículo no es válido")

        vehiculos = await self.obtener_vehiculos()

        vehiculo = next(
            (v for v in vehiculos if v.id == unidad_id),
            None
        )

        if vehiculo is None:
            raise ValueError("El vehículo no existe")

        return vehiculo

    def _obtener_campo(self, vehiculo: Vehicle, campo_id: int):
        if isinstance(campo_id, bool) or not isinstance(campo_id, int) or campo_id <= 0:
            raise ValueError("El ID del campo personalizado no es válido")

        campo = vehiculo.custom_fields.get(str(campo_id))

        if not isinstance(campo, dict):
            raise ValueError("El campo personalizado no existe")

        return campo

    async def listar_campos_personalizados(
        self,
        unidad_id: int
    ) -> list[dict]:
        vehiculo = await self._obtener_vehiculo(unidad_id)

        campos = []

        for campo_id, datos in vehiculo.custom_fields.items():
            if not isinstance(datos, dict):
                continue

            campos.append({
                "id": int(campo_id),
                "nombre": datos.get("n", ""),
                "valor": datos.get("v", "")
            })

        return campos

    async def crear_campo_personalizado(
        self,
        unidad_id: int,
        nombre: str,
        valor: str
    ):
        await self._obtener_vehiculo(unidad_id)

        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del campo es obligatorio")

        if not isinstance(valor, str):
            raise ValueError("El valor del campo debe ser texto")

        resultado = await self.wialon_client.gestionar_campo_personalizado(
            unidad_id=unidad_id,
            campo_id=0,
            accion="create",
            nombre=nombre.strip(),
            valor=valor
        )

        await self.invalidar_cache()

        return resultado

    async def actualizar_campo_personalizado(
        self,
        unidad_id: int,
        campo_id: int,
        nombre: str,
        valor: str
    ):
        vehiculo = await self._obtener_vehiculo(unidad_id)

        self._obtener_campo(vehiculo, campo_id)

        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del campo es obligatorio")

        if not isinstance(valor, str):
            raise ValueError("El valor del campo debe ser texto")

        resultado = await self.wialon_client.gestionar_campo_personalizado(
            unidad_id=unidad_id,
            campo_id=campo_id,
            accion="update",
            nombre=nombre.strip(),
            valor=valor
        )

        await self.invalidar_cache()

        return resultado

    async def eliminar_campo_personalizado(
        self,
        unidad_id: int,
        campo_id: int
    ):
        vehiculo = await self._obtener_vehiculo(unidad_id)

        self._obtener_campo(vehiculo, campo_id)

        resultado = await self.wialon_client.gestionar_campo_personalizado(
            unidad_id=unidad_id,
            campo_id=campo_id,
            accion="delete"
        )

        await self.invalidar_cache()

        return resultado


vehicle_service = VehicleService()
