
import os
from fastapi import APIRouter, Depends

from app.api.dependencies import require_roles
from app.services.vehicle_service import vehicle_service
from app.integrations.wialon_mapper import (
    convertir_conductor,
    convertir_pasajero,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def obtener_resumen_dashboard(
    usuario=Depends(
        require_roles("Administrador", "Operador", "Visualizador")
    )
):
    vehiculos = await vehicle_service.obtener_vehiculos()

    resource_id = int(
        os.getenv("WIALON_RESOURCE_ID", "27668776")
    )

    recursos = await vehicle_service.wialon_client.get_resources()

    recurso = next(
        (
            recurso
            for recurso in recursos
            if recurso.get("id") == resource_id
        ),
        None
    )

    if recurso is None:
        raise RuntimeError(
            "No se encontró el recurso configurado en Wialon"
        )

    datos_conductores = recurso.get("drvrs", {})
    datos_pasajeros = recurso.get("tags", {})

    if not isinstance(datos_conductores, dict):
        raise RuntimeError(
            "Wialon devolvió una estructura inesperada de conductores"
        )

    if not isinstance(datos_pasajeros, dict):
        raise RuntimeError(
            "Wialon devolvió una estructura inesperada de pasajeros"
        )

    conductores = [
        convertir_conductor(datos)
        for datos in datos_conductores.values()
    ]

    pasajeros = [
        convertir_pasajero(datos)
        for datos in datos_pasajeros.values()
    ]

    ids_vehiculos = {
        vehiculo.id
        for vehiculo in vehiculos
    }

    vehiculos_con_conductor = {
        conductor.assigned_unit_id
        for conductor in conductores
        if conductor.assigned_unit_id in ids_vehiculos
    }

    total_vehiculos = len(vehiculos)
    total_con_conductor = len(vehiculos_con_conductor)

    en_movimiento = sum(
        1 for vehiculo in vehiculos
        if vehiculo.status == "en_movimiento"
    )

    detenidos = sum(
        1 for vehiculo in vehiculos
        if vehiculo.status == "detenido"
    )

    sin_senal = sum(
        1 for vehiculo in vehiculos
        if vehiculo.status == "sin_señal"
    )

    vehiculos_con_ubicacion = sum(
        1 for vehiculo in vehiculos
        if vehiculo.latitude is not None
        and vehiculo.longitude is not None
    )

    velocidades = [
        vehiculo.speed
        for vehiculo in vehiculos
        if vehiculo.status == "en_movimiento"
    ]

    velocidad_promedio = (
        round(sum(velocidades) / len(velocidades), 2)
        if velocidades else 0
    )

    ultima_actualizacion = max(
        (
            vehiculo.last_message_time
            for vehiculo in vehiculos
            if vehiculo.last_message_time is not None
        ),
        default=None
    )

    return {
        "total_vehiculos": total_vehiculos,
        "total_conductores": len(conductores),
        "total_pasajeros": len(pasajeros),
        "en_movimiento": en_movimiento,
        "detenidos": detenidos,
        "sin_senal": sin_senal,
        "vehiculos_con_ubicacion": vehiculos_con_ubicacion,
        "velocidad_promedio": velocidad_promedio,
        "vehiculos_con_conductor": total_con_conductor,
        "vehiculos_sin_conductor": (
            total_vehiculos - total_con_conductor
        ),
        "ultima_actualizacion": ultima_actualizacion,
        "distribucion_estados": {
            "en_movimiento": en_movimiento,
            "detenidos": detenidos,
            "sin_senal": sin_senal,
        },
        "distribucion_conductores": {
            "con_conductor": total_con_conductor,
            "sin_conductor": (
                total_vehiculos - total_con_conductor
            ),
        },
    }
