import asyncio

from app.services.vehicle_service import VehicleService


async def main():
    servicio = VehicleService()
    cliente = servicio.wialon_client

    try:
        await cliente.iniciar()

        vehiculos = await servicio.obtener_vehiculos()

        print(f"\nVehículos obtenidos: {len(vehiculos)}")

        for vehiculo in vehiculos[:5]:
            print(
                f"ID: {vehiculo.id} | "
                f"Nombre: {vehiculo.name} | "
                f"Estado: {vehiculo.status} | "
                f"Velocidad: {vehiculo.speed} km/h"
            )

    finally:
        await cliente.cerrar()


if __name__ == "__main__":
    asyncio.run(main())