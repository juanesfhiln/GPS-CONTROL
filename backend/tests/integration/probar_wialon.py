import asyncio
from app.integrations.wialon_client import WialonClient


async def main():
    cliente = WialonClient()

    try:
        await cliente.iniciar()
        await cliente.login()

        vehiculos = await cliente.get_units()

        print(f"Total de vehículos: {len(vehiculos)}")

        for vehiculo in vehiculos[:3]:
            print("\n----------------------------")
            print("ID:", vehiculo.get("id"))
            print("Nombre:", vehiculo.get("nm"))
            print("Campos disponibles:", list(vehiculo.keys()))
            print("Última posición:", vehiculo.get("pos"))
            print("Último mensaje:", vehiculo.get("lmsg"))

    finally:
        await cliente.cerrar()


if __name__ == "__main__":
    asyncio.run(main())