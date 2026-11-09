
from datetime import datetime, timezone

from app.integrations.trip_mock_provider import TripMockProvider
from app.services.vehicle_service import vehicle_service


class TripService:

    def __init__(self):
        self.provider = TripMockProvider()

    async def obtener_historial(
        self,
        unidad_id: int,
        fecha_inicio: datetime,
        fecha_fin: datetime
    ) -> dict:

        if unidad_id <= 0:
            raise ValueError("El ID del vehículo no es válido")

        if fecha_inicio >= fecha_fin:
            raise ValueError("La fecha inicial debe ser anterior a la fecha final")

        if fecha_inicio.tzinfo is None:
            fecha_inicio = fecha_inicio.replace(tzinfo=timezone.utc)

        if fecha_fin.tzinfo is None:
            fecha_fin = fecha_fin.replace(tzinfo=timezone.utc)

        vehiculos = await vehicle_service.obtener_vehiculos()

        vehiculo = next(
            (v for v in vehiculos if v.id == unidad_id),
            None
        )

        if vehiculo is None:
            raise ValueError("El vehículo solicitado no existe")

        viajes = await self.provider.get_trips(
            unidad_id,
            int(fecha_inicio.timestamp()),
            int(fecha_fin.timestamp())
        )

        return {
            "vehicle_id": vehiculo.id,
            "vehicle_name": vehiculo.name,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "total_viajes": len(viajes),
            "viajes": viajes,
            "simulated": True
        }


trip_service = TripService()
