import math

from datetime import datetime, timezone

from app.domain.vehicle import Vehicle
from app.domain.driver import Driver
from app.domain.passenger import Passenger

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

def obtener_estado_comunicacion(ultima_fecha):
    if ultima_fecha is None:
        return "sin_señal"

    ahora = datetime.now(timezone.utc)

    antiguedad = (ahora - ultima_fecha).total_seconds()

    if antiguedad > TIEMPO_SIN_SENAL:
        return "sin_señal"

    return "conectado"


def obtener_estado_posicion(fecha_posicion):
    if fecha_posicion is None:
        return "sin_posicion"

    ahora = datetime.now(timezone.utc)

    antiguedad = (ahora - fecha_posicion).total_seconds()

    if antiguedad > TIEMPO_SIN_SENAL:
        return "antigua"

    return "actualizada"


def obtener_estado(velocidad, estado_posicion):
    if estado_posicion != "actualizada":
        return "sin_señal"

    if velocidad > VELOCIDAD_MINIMA:
        return "en_movimiento"

    return "detenido"

def convertir_vehiculo(datos):
    posicion = datos.get("pos") or {}
    ultimo_mensaje = datos.get("lmsg") or {}

    latitud = numero_valido(posicion.get("y"))
    longitud = numero_valido(posicion.get("x"))

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

    if latitud is None or longitud is None:
        fecha_posicion = None

    comunicacion = obtener_estado_comunicacion(fecha_mensaje)
    posicion_estado = obtener_estado_posicion(fecha_posicion)

    estado = obtener_estado(
        velocidad,
        posicion_estado
    )

    campos_personalizados = datos.get("flds") or {}

    if not isinstance(campos_personalizados, dict):
        campos_personalizados = {}

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
        status=estado,
        communication_status=comunicacion,
        position_status=posicion_estado,
        custom_fields=campos_personalizados
    )

def convertir_conductor(datos):
    campos_personalizados = datos.get("jp") or {}

    campos_personalizados = {
        str(clave): valor
        for clave, valor in campos_personalizados.items()
        if isinstance(valor, str)
    }

    vehiculo_asignado = datos.get("bu")

    if not isinstance(vehiculo_asignado, int) or vehiculo_asignado == 0:
        vehiculo_asignado = None

    return Driver(
        id=int(datos["id"]),
        name=datos.get("n") or "Sin nombre",
        code=datos.get("c"),
        phone=datos.get("p"),
        description=datos.get("ds"),
        assigned_unit_id=vehiculo_asignado,
        custom_fields=campos_personalizados
    )



def convertir_pasajero(datos: dict) -> Passenger:
    if not isinstance(datos, dict):
        raise ValueError("Los datos del pasajero no son válidos")

    jp = datos.get("jp", {})

    if jp is None:
        jp = {}

    if not isinstance(jp, dict):
        raise ValueError("Los campos personalizados no son válidos")

    if not all(
        isinstance(clave, str) and isinstance(valor, str)
        for clave, valor in jp.items()
    ):
        raise ValueError("Los campos personalizados contienen valores no válidos")

    campos_personalizados = dict(jp)

    telefono_interno = campos_personalizados.pop("_telefono", "")
    telefono = datos.get("p") or telefono_interno or ""

    if not isinstance(telefono, str):
        telefono = ""

    vehiculo_asignado = datos.get("bu")

    if (
        isinstance(vehiculo_asignado, bool)
        or not isinstance(vehiculo_asignado, int)
        or vehiculo_asignado <= 0
    ):
        vehiculo_asignado = None

    pasajero_id = datos.get("id")

    if (
        isinstance(pasajero_id, bool)
        or not isinstance(pasajero_id, int)
        or pasajero_id <= 0
    ):
        raise ValueError("El ID del pasajero no es válido")

    return Passenger(
        id=pasajero_id,
        name=datos.get("n", ""),
        code=datos.get("c", ""),
        phone=telefono,
        assigned_unit_id=vehiculo_asignado,
        custom_fields=campos_personalizados
    )
