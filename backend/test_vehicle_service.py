import asyncio

from app.services.vehicle_service import VehicleService


async def main():
    servicio = VehicleService()

    vehiculos = await servicio.obtener_vehiculos()

    print(f"\nVehículos obtenidos: {len(vehiculos)}")

    for vehiculo in vehiculos[:5]:
        print(
            f"ID: {vehiculo.id} | "
            f"Nombre: {vehiculo.name} | "
            f"Estado: {vehiculo.status} | "
            f"Velocidad: {vehiculo.speed} km/h"
        )


if __name__ == "__main__":
    asyncio.run(main())