import math

from datetime import datetime, timezone

from app.domain.vehicle import Vehicle


TIEMPO_SIN_SENAL = 300
VELOCIDAD_MINIMA = 3


def convertir_fecha(timestamp):
    if timestamp is None:
        return None

    try:
        fecha = datetime.fromtimestamp(
            float(timestamp),
            tz=timezone.utc
        )
    except (TypeError, ValueError, OverflowError, OSError):
        return None

    if fecha > datetime.now(timezone.utc):
        return None

    return fecha


def numero_valido(valor):
    try:
        numero = float(valor)

        if not math.isfinite(numero):
            return None

        return numero

    except (TypeError, ValueError):
        return None


def obtener_rumbo_cardinal(rumbo):
    if rumbo is None:
        return None

    direcciones = [
        "Norte",
        "Noreste",
        "Este",
        "Sureste",
        "Sur",
        "Suroeste",
        "Oeste",
        "Noroeste"
    ]

    indice = int((rumbo + 22.5) // 45) % 8

    return direcciones[indice]


def obtener_estado(velocidad, ultima_fecha, fecha_posicion):
    if ultima_fecha is None or fecha_posicion is None:
        return "sin_señal"

    ahora = datetime.now(timezone.utc)

    antiguedad_mensaje = (
        ahora - ultima_fecha
    ).total_seconds()

    antiguedad_posicion = (
        ahora - fecha_posicion
    ).total_seconds()

    if antiguedad_mensaje > TIEMPO_SIN_SENAL:
        return "sin_señal"

    if antiguedad_posicion > TIEMPO_SIN_SENAL:
        return "sin_señal"

    if velocidad > VELOCIDAD_MINIMA:
        return "en_movimiento"

    return "detenido"


def convertir_vehiculo(datos):
    posicion = datos.get("pos") or {}
    ultimo_mensaje = datos.get("lmsg") or {}

    latitud = numero_valido(posicion.get("y"))
    longitud = numero_valido(posicion.get("x"))

    # Las dos coordenadas deben existir y ser válidas.
    if (
        latitud is None
        or longitud is None
        or not -90 <= latitud <= 90
        or not -180 <= longitud <= 180
    ):
        latitud = None
        longitud = None

    velocidad = numero_valido(posicion.get("s"))
    velocidad = max(0, velocidad) if velocidad is not None else 0

    rumbo = numero_valido(posicion.get("c"))

    if rumbo is not None:
        rumbo = int(rumbo) % 360
        
    rumbo_cardinal = obtener_rumbo_cardinal(rumbo)

    altitud = numero_valido(posicion.get("z"))

    fecha_posicion = convertir_fecha(posicion.get("t"))
    fecha_mensaje = convertir_fecha(ultimo_mensaje.get("t"))

    # Sin coordenadas, no podemos considerar la posición reciente.
    if latitud is None or longitud is None:
        fecha_posicion = None

    estado = obtener_estado(
        velocidad,
        fecha_mensaje,
        fecha_posicion
    )

    return Vehicle(
        id=datos["id"],
        name=datos.get("nm") or "Sin nombre",
        latitude=latitud,
        longitude=longitud,
        speed=velocidad,
        heading=rumbo,
        heading_cardinal=rumbo_cardinal,
        altitude=altitud,
        position_time=fecha_posicion,
        last_message_time=fecha_mensaje,
        status=estado
    )