import os
import asyncio
import logging

from app.services.vehicle_service import vehicle_service
from app.integrations.wialon_mapper import convertir_conductor
from app.domain.driver import Driver

logger = logging.getLogger(__name__)

class DriverService:

    def __init__(self, wialon_client):
        self.wialon_client = wialon_client
        self.resource_id = int(
            os.getenv("WIALON_RESOURCE_ID", "27668776")
        )

    async def obtener_conductores(self) -> list[Driver]:

        recursos = await self.wialon_client.get_resources()

        recurso = next(
            (
                r for r in recursos
                if r.get("id") == self.resource_id
            ),
            None
        )

        if recurso is None:
            raise RuntimeError(
                "No se encontró el recurso configurado en Wialon"
            )

        conductores = recurso.get("drvrs", {})

        for conductor in conductores.values():
            
            logger.warning(
                "Conductor Wialon ID=%s, bu=%r",
                conductor.get("id"),
                conductor.get("bu")
            )

        return [
            convertir_conductor(datos)
            for datos in conductores.values()
        ]

    async def obtener_asignaciones(self):
        conductores = await self.obtener_conductores()

        asignaciones = [
            {
                "unit_id": conductor.assigned_unit_id,
                "driver_id": str(conductor.id),
                "name": conductor.name,
                "phone": conductor.phone or ""
            }
            for conductor in conductores
            if conductor.assigned_unit_id is not None
            and conductor.assigned_unit_id > 0
        ]

        return {
            "total": len(asignaciones),
            "resultados": asignaciones,
            "completa": True,
            "vehiculos_con_error": 0
        }
    
    async def asignar_conductor(self, driver_id: int, unit_id: int):
        if driver_id <= 0 or unit_id <= 0:
            raise ValueError("El ID del conductor o vehículo no es válido")

        conductores = await self.obtener_conductores()

        conductor = next(
            (c for c in conductores if c.id == driver_id),
            None
        )

        if conductor is None:
            raise ValueError("El conductor no existe en el recurso")

        unidades = await self.wialon_client.get_units()

        if not any(u.get("id") == unit_id for u in unidades):
            raise ValueError("El vehículo no existe en Wialon")

        consulta = await self.obtener_asignaciones()

        if not consulta["completa"]:
            raise RuntimeError(
                "No se pueden validar las asignaciones porque la consulta está incompleta"
            )

        asignaciones = consulta["resultados"]

        if any(int(a["driver_id"]) == driver_id for a in asignaciones):
            raise ValueError("El conductor ya está asignado a otro vehículo")

        if any(a["unit_id"] == unit_id for a in asignaciones):
            raise ValueError("El vehículo ya tiene un conductor asignado")

        return await self.wialon_client.bind_unit_driver(
            resource_id=self.resource_id,
            unit_id=unit_id,
            driver_id=driver_id,
            asignar=True
        )

    async def desvincular_conductor(self, driver_id: int, unit_id: int):
        if driver_id <= 0 or unit_id <= 0:
            raise ValueError("El ID del conductor o vehículo no es válido")

        consulta = await self.obtener_asignaciones()

        if not consulta["completa"]:
            raise RuntimeError(
                "No se pueden validar las asignaciones porque la consulta está incompleta"
            )

        asignacion = next(
            (
                a for a in consulta["resultados"]
                if int(a["driver_id"]) == driver_id
                and a["unit_id"] == unit_id
            ),
            None
        )

        if asignacion is None:
            raise ValueError(
                "El conductor no está asignado a este vehículo"
            )

        return await self.wialon_client.bind_unit_driver(
            resource_id=self.resource_id,
            unit_id=unit_id,
            driver_id=driver_id,
            asignar=False
        )

    async def crear_conductor(
        self,
        nombre: str,
        codigo: str = "",
        telefono: str = "",
        descripcion: str = ""
    ):
        conductores = await self.obtener_conductores()

        codigo = codigo.strip()
        telefono = telefono.strip()

        if codigo and any(
            conductor.code
            and conductor.code.strip().lower() == codigo.lower()
            for conductor in conductores
        ):
            raise ValueError("Ya existe un conductor con ese código")

        if telefono and any(
            conductor.phone
            and conductor.phone.strip() == telefono
            for conductor in conductores
        ):
            raise ValueError("Ya existe un conductor con ese teléfono")
        
        print("Preparando creación de conductor")

        resultado = await self.wialon_client.crear_conductor(
            resource_id=self.resource_id,
            nombre=nombre,
            codigo=codigo,
            telefono=telefono,
            descripcion=descripcion
        )

        if (
            not isinstance(resultado, list)
            or len(resultado) != 2
            or not isinstance(resultado[0], int)
            or resultado[0] <= 0
            or not isinstance(resultado[1], dict)
        ):
            raise RuntimeError(
                "Wialon devolvió una respuesta inesperada al crear el conductor"
            )

        return resultado[0]

    async def actualizar_conductor(
        self,
        driver_id: int,
        nombre: str,
        codigo: str = "",
        telefono: str = "",
        descripcion: str = ""
    ):
        conductores = await self.obtener_conductores()

        conductor_actual = next(
            (
                conductor
                for conductor in conductores
                if conductor.id == driver_id
            ),
            None
        )

        if conductor_actual is None:
            raise ValueError("No se encontró el conductor")

        codigo = codigo.strip()
        telefono = telefono.strip()

        if codigo and any(
            conductor.id != driver_id
            and conductor.code
            and conductor.code.strip().lower() == codigo.lower()
            for conductor in conductores
        ):
            raise ValueError("Ya existe otro conductor con ese código")

        if telefono and any(
            conductor.id != driver_id
            and conductor.phone
            and conductor.phone.strip() == telefono
            for conductor in conductores
        ):
            raise ValueError("Ya existe otro conductor con ese teléfono")

        resultado = await self.wialon_client.actualizar_conductor(
            resource_id=self.resource_id,
            driver_id=driver_id,
            nombre=nombre,
            codigo=codigo,
            telefono=telefono,
            descripcion=descripcion,
            campos_personalizados=conductor_actual.custom_fields
        )

        if (
            not isinstance(resultado, list)
            or len(resultado) != 2
            or not isinstance(resultado[0], int)
            or resultado[0] != driver_id
            or not isinstance(resultado[1], dict)
        ):
            raise RuntimeError(
                "Wialon devolvió una respuesta inesperada al actualizar el conductor"
            )

        return resultado[0]

    async def eliminar_conductor(self, driver_id: int):
        conductores = await self.obtener_conductores()

        conductor = next(
            (
                conductor
                for conductor in conductores
                if conductor.id == driver_id
            ),
            None
        )

        if conductor is None:
            raise ValueError("No se encontró el conductor")

        if conductor.assigned_unit_id is not None:
            raise ValueError(
                "No se puede eliminar un conductor asignado a un vehículo"
            )

        resultado = await self.wialon_client.eliminar_conductor(
            resource_id=self.resource_id,
            driver_id=driver_id
        )

        if (
            not isinstance(resultado, list)
            or len(resultado) != 2
            or resultado[0] != driver_id
            or resultado[1] is not None
        ):
            raise RuntimeError(
                "Wialon devolvió una respuesta inesperada al eliminar el conductor"
            )

        return driver_id
driver_service = DriverService(
    vehicle_service.wialon_client
)