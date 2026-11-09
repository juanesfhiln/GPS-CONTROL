from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.dependencies import require_roles


def crear_usuario(rol):
    return SimpleNamespace(
        rol=SimpleNamespace(nombre=rol)
    )


@pytest.mark.parametrize(
    "rol",
    ["Administrador", "Operador"]
)
def test_administrador_y_operador_pueden_editar(rol):
    verificar_rol = require_roles("Administrador", "Operador")
    usuario = crear_usuario(rol)

    resultado = verificar_rol(usuario)

    assert resultado is usuario


def test_visualizador_no_puede_editar():
    verificar_rol = require_roles("Administrador", "Operador")
    usuario = crear_usuario("Visualizador")

    with pytest.raises(HTTPException) as error:
        verificar_rol(usuario)

    assert error.value.status_code == 403
    assert error.value.detail == "No tienes permisos para realizar esta operación"