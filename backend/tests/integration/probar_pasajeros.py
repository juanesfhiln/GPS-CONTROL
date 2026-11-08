
import asyncio

from app.services.vehicle_service import vehicle_service


async def main():
    cliente = vehicle_service.wialon_client
    await cliente.iniciar()

    try:
        recursos = await cliente.get_resources()

        recurso_id = int(__import__("os").getenv(
            "WIALON_RESOURCE_ID", "27668776"
        ))

        recurso = next(
            r for r in recursos if r.get("id") == recurso_id
        )

        etiquetas = recurso.get("tags", {})

        for etiqueta in list(etiquetas.values())[:10]:
            print({
                "id": etiqueta.get("id"),
                "nombre": etiqueta.get("n"),
                "bu": etiqueta.get("bu"),
                "tipo_bu": type(etiqueta.get("bu")).__name__,
                "pu": etiqueta.get("pu"),
                "bt": etiqueta.get("bt")
            })

    finally:
        await cliente.cerrar()


if __name__ == "__main__":
    asyncio.run(main())
