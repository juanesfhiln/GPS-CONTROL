
from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.dependencies import require_roles
from app.schemas.vehicle import VehicleResponse
from app.services.vehicle_service import vehicle_service


router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("/")
async def listar_vehiculos(
    buscar: str | None = Query(default=None, min_length=1),
    estado: str | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=10, ge=1, le=100),
    usuario=Depends(
        require_roles("Administrador", "Operador", "Visualizador")
    )
):
    estados_validos = [
        "en_movimiento",
        "detenido",
        "sin_señal"
    ]

    if estado is not None and estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail="El estado indicado no es válido"
        )

    vehiculos = await vehicle_service.obtener_vehiculos()

    if buscar is not None:
        termino = buscar.strip().lower()

        if not termino:
            raise HTTPException(
                status_code=400,
                detail="El término de búsqueda no puede estar vacío"
            )

        vehiculos = [
            v for v in vehiculos
            if termino in v.name.lower() or termino in str(v.id)
        ]

    if estado:
        vehiculos = [
            v for v in vehiculos
            if v.status == estado
        ]

    total = len(vehiculos)
    inicio = (pagina - 1) * limite
    fin = inicio + limite

    vehiculos_paginados = vehiculos[inicio:fin]

    return {
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": (total + limite - 1) // limite,
        "resultados": [
            VehicleResponse.model_validate(v)
            for v in vehiculos_paginados
        ]
    }
