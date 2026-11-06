
import asyncio

from app.integrations.wialon_client import WialonClient


async def main():
    cliente = WialonClient()

    # Primera autenticación.
    await cliente.login()
    print("Primera autenticación: OK")

    # Simular que la sesión anterior dejó de ser válida.
    cliente.session_id = "SESION_INVALIDA_DE_PRUEBA"

    # La consulta debería detectar el error 1,
    # renovar la sesión y reintentar.
    vehiculos = await cliente.get_units()

    print("Consulta después de renovar: OK")
    print("Total de vehículos:", len(vehiculos))


if __name__ == "__main__":
    asyncio.run(main())
