from datetime import datetime, timedelta, timezone

from app.integrations.wialon_mapper import (
    obtener_estado_comunicacion,
    obtener_estado_posicion,
    obtener_estado
)


def test_comunicacion_reciente():
    fecha = datetime.now(timezone.utc) - timedelta(seconds=60)

    assert obtener_estado_comunicacion(fecha) == "conectado"


def test_comunicacion_antigua():
    fecha = datetime.now(timezone.utc) - timedelta(seconds=600)

    assert obtener_estado_comunicacion(fecha) == "sin_señal"


def test_comunicacion_inexistente():
    assert obtener_estado_comunicacion(None) == "sin_señal"


def test_posicion_actualizada():
    fecha = datetime.now(timezone.utc) - timedelta(seconds=60)

    assert obtener_estado_posicion(fecha) == "actualizada"


def test_posicion_antigua():
    fecha = datetime.now(timezone.utc) - timedelta(seconds=600)

    assert obtener_estado_posicion(fecha) == "antigua"


def test_posicion_inexistente():
    assert obtener_estado_posicion(None) == "sin_posicion"


def test_vehiculo_en_movimiento():
    assert obtener_estado(24, "actualizada") == "en_movimiento"


def test_vehiculo_detenido():
    assert obtener_estado(0, "actualizada") == "detenido"


def test_posicion_antigua_no_es_movimiento():
    assert obtener_estado(24, "antigua") == "sin_señal"