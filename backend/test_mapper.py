import asyncio
from datetime import datetime, timezone

from app.integrations.wialon_client import WialonClient
from app.integrations.wialon_mapper import convertir_vehiculo


TIEMPO_SIN_SENAL = 300


async def main():
    cliente = WialonClient()

    await cliente.login()
    datos_vehiculos = await cliente.get_units()

    total = len(datos_vehiculos)

    coordenadas_validas = 0
    coordenadas_incompletas = 0
    coordenadas_invalidas = 0
    posiciones_antiguas = 0
    mensajes_antiguos = 0
    errores = 0

    estados = {
        "en_movimiento": 0,
        "detenido": 0,
        "sin_señal": 0
    }

    ahora = datetime.now(timezone.utc)

    print(f"\nTotal de vehículos recibidos: {total}")

    for datos in datos_vehiculos:
        try:
            vehiculo = convertir_vehiculo(datos)

            latitud = vehiculo.latitude
            longitud = vehiculo.longitude

            # Comprobar coordenadas
            if latitud is None and longitud is None:
                coordenadas_incompletas += 1

            elif latitud is None or longitud is None:
                coordenadas_incompletas += 1

            elif not (-90 <= latitud <= 90 and -180 <= longitud <= 180):
                coordenadas_invalidas += 1

            else:
                coordenadas_validas += 1

            # Comprobar antigüedad de la posición
            if vehiculo.position_time is None:
                posiciones_antiguas += 1
            else:
                antiguedad_posicion = (
                    ahora - vehiculo.position_time
                ).total_seconds()

                if antiguedad_posicion > TIEMPO_SIN_SENAL:
                    posiciones_antiguas += 1

            # Comprobar antigüedad del último mensaje
            if vehiculo.last_message_time is None:
                mensajes_antiguos += 1
            else:
                antiguedad_mensaje = (
                    ahora - vehiculo.last_message_time
                ).total_seconds()

                if antiguedad_mensaje > TIEMPO_SIN_SENAL:
                    mensajes_antiguos += 1

            estados[vehiculo.status] += 1

        except Exception as error:
            errores += 1
            print(
                f"Error procesando vehículo "
                f"{datos.get('id')}: {error}"
            )

    print("\n========== DIAGNÓSTICO DE POSICIONES ==========")

    for datos in datos_vehiculos:
        posicion = datos.get("pos") or {}
        mensaje = datos.get("lmsg") or {}

        fecha_pos = posicion.get("t")
        fecha_msg = mensaje.get("t")

        print(
            f"ID: {datos.get('id')} | "
            f"Nombre: {datos.get('nm')} | "
            f"Flags posición: {posicion.get('f')} | "
            f"Fecha posición: {fecha_pos} | "
            f"Fecha mensaje: {fecha_msg} | "
            f"Velocidad: {posicion.get('s')} | "
            f"Coordenadas: ({posicion.get('y')}, {posicion.get('x')})"
        )

    print("\n========== RESULTADOS ==========")
    print(f"Total recibidos: {total}")
    print(f"Coordenadas válidas: {coordenadas_validas}")
    print(f"Coordenadas incompletas: {coordenadas_incompletas}")
    print(f"Coordenadas inválidas: {coordenadas_invalidas}")
    print(f"Posiciones antiguas o inexistentes: {posiciones_antiguas}")
    print(f"Mensajes antiguos o inexistentes: {mensajes_antiguos}")
    print(f"Errores de transformación: {errores}")

    print("\n========== ESTADOS ==========")
    for estado, cantidad in estados.items():
        print(f"{estado}: {cantidad}")

    print("\n========== MUESTRA ==========")

    for datos in datos_vehiculos[:5]:
        vehiculo = convertir_vehiculo(datos)

        print(
            f"ID: {vehiculo.id} | "
            f"Nombre: {vehiculo.name} | "
            f"Latitud: {vehiculo.latitude} | "
            f"Longitud: {vehiculo.longitude} | "
            f"Velocidad: {vehiculo.speed} km/h | "
            f"Estado: {vehiculo.status}\n"
            f"Rumbo numérico: {vehiculo.heading}°\n"
            f"Rumbo cardinal: {vehiculo.heading_cardinal}"
        )


if __name__ == "__main__":
    asyncio.run(main())