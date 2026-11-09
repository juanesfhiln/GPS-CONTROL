
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import require_roles
from app.schemas.trip import TripHistoryResponse
from app.services.trip_service import trip_service

router = APIRouter()


@router.get("/{unidad_id}/history", response_model=TripHistoryResponse)
async def obtener_historial_viajes(
    unidad_id: int,
    fecha_inicio: datetime = Query(...),
    fecha_fin: datetime = Query(...),
    usuario=Depends(
        require_roles("Administrador", "Operador", "Visualizador")
    )
):
    try:
        return await trip_service.obtener_historial(
            unidad_id,
            fecha_inicio,
            fecha_fin
        )
    except ValueError as error:
        mensaje = str(error)

        if mensaje == "El vehículo solicitado no existe":
            raise HTTPException(status_code=404, detail=mensaje)

        raise HTTPException(status_code=400, detail=mensaje)
