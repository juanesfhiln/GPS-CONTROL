
import httpx

from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.api.dependencies import require_roles
from app.schemas.vehicle import VehicleResponse, VehicleCustomFieldUpdate
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
        termino = buscar.strip().casefold()

        if not termino:
            raise HTTPException(
                status_code=400,
                detail="El término de búsqueda no puede estar vacío"
            )

        def coincide_placa(vehiculo):
            for campo in vehiculo.custom_fields.values():
                if not isinstance(campo, dict):
                    continue

                nombre = str(campo.get("n", "")).strip().casefold()
                valor = str(campo.get("v", "")).strip().casefold()

                if nombre == "placa" and termino in valor:
                    return True

            return False

        vehiculos = [
            v for v in vehiculos
            if (
                termino in v.name.casefold()
                or termino in str(v.id)
                or coincide_placa(v)
            )
        ]

    if estado:
        vehiculos = [
            v for v in vehiculos
            if v.status == estado
        ]

    total = len(vehiculos)
    inicio = (pagina - 1) * limite
    fin = inicio + limite

    return {
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": (total + limite - 1) // limite,
        "resultados": [
            VehicleResponse.model_validate(v)
            for v in vehiculos[inicio:fin]
        ]
    }


@router.get("/{unidad_id}/custom-fields")
async def listar_campos_personalizados(
    unidad_id: int,
    usuario=Depends(
        require_roles("Administrador", "Operador", "Visualizador")
    )
):
    try:
        return await vehicle_service.listar_campos_personalizados(
            unidad_id=unidad_id
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except (RuntimeError, httpx.HTTPError):
        raise HTTPException(
            status_code=502,
            detail="No fue posible consultar los campos en Wialon"
        )


@router.post(
    "/{unidad_id}/custom-fields",
    status_code=status.HTTP_201_CREATED
)
async def crear_campo_personalizado(
    unidad_id: int,
    datos: VehicleCustomFieldUpdate,
    usuario=Depends(
        require_roles("Administrador", "Operador")
    )
):
    try:
        resultado = await vehicle_service.crear_campo_personalizado(
            unidad_id=unidad_id,
            nombre=datos.nombre,
            valor=datos.valor
        )

        return {
            "mensaje": "Campo personalizado creado correctamente",
            "resultado": resultado
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except (RuntimeError, httpx.HTTPError):
        raise HTTPException(
            status_code=502,
            detail="No fue posible crear el campo en Wialon"
        )


@router.put("/{unidad_id}/custom-fields/{campo_id}")
async def actualizar_campo_personalizado(
    unidad_id: int,
    campo_id: int,
    datos: VehicleCustomFieldUpdate,
    usuario=Depends(
        require_roles("Administrador", "Operador")
    )
):
    try:
        resultado = await vehicle_service.actualizar_campo_personalizado(
            unidad_id=unidad_id,
            campo_id=campo_id,
            nombre=datos.nombre,
            valor=datos.valor
        )

        return {
            "mensaje": "Campo personalizado actualizado correctamente",
            "resultado": resultado
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except (RuntimeError, httpx.HTTPError):
        raise HTTPException(
            status_code=502,
            detail="No fue posible actualizar el campo en Wialon"
        )


@router.delete("/{unidad_id}/custom-fields/{campo_id}")
async def eliminar_campo_personalizado(
    unidad_id: int,
    campo_id: int,
    usuario=Depends(
        require_roles("Administrador", "Operador")
    )
):
    try:
        resultado = await vehicle_service.eliminar_campo_personalizado(
            unidad_id=unidad_id,
            campo_id=campo_id
        )

        return {
            "mensaje": "Campo personalizado eliminado correctamente",
            "resultado": resultado
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except (RuntimeError, httpx.HTTPError):
        raise HTTPException(
            status_code=502,
            detail="No fue posible eliminar el campo en Wialon"
        )
