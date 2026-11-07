from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.api.dependencies import require_roles
from app.services.vehicle_service import vehicle_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def obtener_resumen_dashboard(
    usuario=Depends(
        require_roles("Administrador", "Operador", "Visualizador")
    )
):
    vehiculos = await vehicle_service.obtener_vehiculos()

    total = len(vehiculos)

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
        "total_vehiculos": total,
        "en_movimiento": en_movimiento,
        "detenidos": detenidos,
        "sin_senal": sin_senal,
        "vehiculos_con_ubicacion": vehiculos_con_ubicacion,
        "velocidad_promedio": velocidad_promedio,
        "ultima_actualizacion": ultima_actualizacion,
    }