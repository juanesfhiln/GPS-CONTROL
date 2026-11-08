
import pytest

from app.integrations.wialon_mapper import (
    convertir_vehiculo,
    convertir_conductor,
    convertir_pasajero
)


def test_convertir_pasajero_correctamente():
    datos = {
        "id": 101,
        "n": "Juan Pérez",
        "c": "PAS-001",
        "p": "3001234567",
        "bu": 12345,
        "jp": {
            "Área": "Norte",
            "Turno": "Mañana"
        }
    }

    pasajero = convertir_pasajero(datos)

    assert pasajero.id == 101
    assert pasajero.name == "Juan Pérez"
    assert pasajero.code == "PAS-001"
    assert pasajero.phone == "3001234567"
    assert pasajero.assigned_unit_id == 12345
    assert pasajero.custom_fields == {
        "Área": "Norte",
        "Turno": "Mañana"
    }


def test_convertir_pasajero_sin_campos_personalizados():
    datos = {
        "id": 102,
        "n": "María Gómez",
        "c": "",
        "p": "",
        "bu": 0
    }

    pasajero = convertir_pasajero(datos)

    assert pasajero.custom_fields == {}
    assert pasajero.assigned_unit_id is None


def test_convertir_pasajero_rechaza_jp_invalido():
    datos = {
        "id": 103,
        "n": "Carlos",
        "jp": []
    }

    with pytest.raises(ValueError):
        convertir_pasajero(datos)


def test_convertir_pasajero_rechaza_valores_booleanos():
    datos = {
        "id": 104,
        "n": "Ana",
        "jp": {
            "Activo": True
        }
    }

    with pytest.raises(ValueError):
        convertir_pasajero(datos)


def test_convertir_pasajero_rechaza_id_invalido():
    datos = {
        "id": 0,
        "n": "Pedro"
    }

    with pytest.raises(ValueError):
        convertir_pasajero(datos)


def test_convertir_pasajero_rechaza_datos_no_diccionario():
    with pytest.raises(ValueError):
        convertir_pasajero(None)


def test_convertir_pasajero_ignora_vehiculo_invalido():
    datos = {
        "id": 105,
        "n": "Laura",
        "bu": True
    }

    pasajero = convertir_pasajero(datos)

    assert pasajero.assigned_unit_id is None
