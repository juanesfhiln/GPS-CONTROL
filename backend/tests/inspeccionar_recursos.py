import asyncio
from app.integrations.wialon_client import WialonClient
from app.integrations.wialon_mapper import convertir_conductor

async def main():
    client = WialonClient()

    try:
        await client.iniciar()
        recursos = await client.get_resources()

        recurso = next(
            r for r in recursos
            if r.get("id") == 27668776
        )

        # for nombre, registros in [
        #     ("CONDUCTORES", recurso.get("drvrs", {}).values()),
        #     ("PASAJEROS", recurso.get("tags", {}).values())
        # ]:
        #     registros = list(registros)
        #     asignados = sum(1 for r in registros if r.get("bu"))

        #     campos_jp = sorted({
        #         campo
        #         for registro in registros
        #         for campo in registro.get("jp", {})
        #     })

        #     print(f"\n{nombre}")
        #     print(f"Total: {len(registros)}")
        #     print(f"Asignados: {asignados}")
        #     print(f"Sin asignar: {len(registros) - asignados}")
        #     print(f"Campos personalizados: {campos_jp}")

        # for nombre, registros in [
        #     ("CONDUCTORES", recurso.get("drvrs", {}).values()),
        #     ("PASAJEROS", recurso.get("tags", {}).values())
        # ]:
        #     registro = next(
        #         (r for r in registros if r.get("jp")),
        #         None
        #     )

        #     print(f"\n--- ESTRUCTURA JP: {nombre} ---")

        #     if not registro:
        #         print("No hay registros con campos personalizados")
        #         continue

        #     for clave, valor in registro.get("jp", {}).items():
        #         print(
        #             f"Campo: {clave} | "
        #             f"Tipo: {type(valor).__name__}"
        #         )

        # conductores = recurso.get("drvrs", {})

        # conductor_asignado = next(
        #     (
        #         conductor
        #         for conductor in conductores.values()
        #         if conductor.get("bu")
        #     ),
        #     None
        # )

        # if conductor_asignado:
        #     print("\nESTRUCTURA DE ASIGNACIÓN")

        #     for campo in ["id", "bu", "pu", "bt", "jp"]:
        #         valor = conductor_asignado.get(campo)

        #         print(
        #             f"{campo}: "
        #             f"{type(valor).__name__}"
        #         )

        # conductor = next(iter(conductores.values()))

        # for campo in ["n", "c", "p", "ds", "bu", "jp"]:
        #     valor = conductor.get(campo)
        #     print(f"{campo}: {type(valor).__name__}")

        print("\n--- VALIDACIÓN DEL MAPEADOR ---")

        conductores = recurso.get("drvrs", {}).values()

        conductores_convertidos = [
            convertir_conductor(conductor)
            for conductor in conductores
        ]

        print(f"Conductores originales: {len(conductores)}")
        print(f"Conductores convertidos: {len(conductores_convertidos)}")

        for conductor in conductores_convertidos:
            print(
                f"ID: {conductor.id} | "
                f"Nombre: {conductor.name} | "
                f"Asignado: {conductor.assigned_unit_id is not None} | "
                f"Campos personalizados: {len(conductor.custom_fields)}"
            )
    finally:
        await client.cerrar()



if __name__ == "__main__":
    asyncio.run(main())
