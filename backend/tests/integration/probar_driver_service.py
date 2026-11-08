import asyncio

from app.services.driver_service import driver_service


async def main():
    client = driver_service.wialon_client

    try:
        await client.iniciar()

        conductores = await driver_service.obtener_conductores()

        print("\n--- VALIDACIÓN DRIVER SERVICE ---")
        print(f"Total de conductores: {len(conductores)}")

        asignados = sum(
            1 for conductor in conductores
            if conductor.assigned_unit_id is not None
        )

        print(f"Conductores asignados: {asignados}")
        print(f"Conductores sin asignar: {len(conductores) - asignados}")

        print("\nServicio ejecutado correctamente.")

    except Exception as error:
        print(f"Error al consultar conductores: {error}")
        raise

    finally:
        await client.cerrar()


if __name__ == "__main__":
    asyncio.run(main())