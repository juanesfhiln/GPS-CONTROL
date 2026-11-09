from fastapi import APIRouter, Depends, Query, HTTPException, status, Request

from app.api.dependencies import require_roles
from app.schemas.driver import DriverResponse, DriverCreate, DriverUpdate
from app.services.driver_service import driver_service
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.services.audit_service import audit_service

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/drivers",
    tags=["Conductores"]
)


@router.get("/")
async def listar_conductores(
    buscar: str | None = Query(default=None, min_length=1),
    id_conductor: int | None = Query(default=None, ge=1),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=10, ge=1, le=100),
    usuario=Depends(
        require_roles(
            "Administrador",
            "Operador",
            "Visualizador"
        )
    )
):
    try:
        conductores = await driver_service.obtener_conductores()

        if buscar is not None:
            termino = buscar.strip().lower()

            if not termino:
                raise HTTPException(
                    status_code=400,
                    detail="El término de búsqueda no puede estar vacío"
                )

            conductores = [
                conductor
                for conductor in conductores
                if termino in conductor.name.lower()
                or termino in (conductor.code or "").lower()
            ]

        if id_conductor is not None:
            conductores = [
                conductor
                for conductor in conductores
                if conductor.id == id_conductor
            ]

        total = len(conductores)
        inicio = (pagina - 1) * limite
        fin = inicio + limite

        resultados = conductores[inicio:fin]

        return {
            "total": total,
            "pagina": pagina,
            "limite": limite,
            "total_paginas": (total + limite - 1) // limite,
            "resultados": [
                DriverResponse.model_validate(conductor)
                for conductor in resultados
            ]
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="No fue posible consultar los conductores en Wialon"
        )

@router.get("/asignaciones")
async def listar_asignaciones(
    usuario=Depends(
        require_roles(
            "Administrador",
            "Operador",
            "Visualizador"
        )
    )
):
    try:

        resultado = await driver_service.obtener_asignaciones()
        return resultado

    except Exception:
        logger.exception(
            "Error al consultar las asignaciones de conductores"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible consultar las asignaciones en Wialon"
        )


@router.post("/{driver_id}/asignar/{unit_id}")
async def asignar_conductor(
    driver_id: int,
    unit_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles("Administrador", "Operador"))
):
    try:
        await driver_service.asignar_conductor(
            driver_id=driver_id,
            unit_id=unit_id
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="ASSIGN",
            modulo="CONDUCTORES",
            descripcion=f"Asignación del conductor ID {driver_id} al vehículo ID {unit_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Conductor asignado correctamente",
            "driver_id": driver_id,
            "unit_id": unit_id
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Error inesperado al asignar un conductor"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible asignar el conductor en Wialon"
        )


@router.delete("/{driver_id}/desvincular/{unit_id}")
async def desvincular_conductor(
    driver_id: int,
    unit_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles("Administrador", "Operador"))
):
    try:
        await driver_service.desvincular_conductor(
            driver_id=driver_id,
            unit_id=unit_id
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="UNASSIGN",
            modulo="CONDUCTORES",
            descripcion=f"Desvinculación del conductor ID {driver_id} del vehículo ID {unit_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Conductor desvinculado correctamente",
            "driver_id": driver_id,
            "unit_id": unit_id
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Error inesperado al desvincular un conductor"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible desvincular el conductor en Wialon"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_conductor(
    datos: DriverCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles("Administrador", "Operador"))
):
    try:
        resultado = await driver_service.crear_conductor(
            nombre=datos.name,
            codigo=datos.code,
            telefono=datos.phone,
            descripcion=datos.description
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="CREATE",
            modulo="CONDUCTORES",
            descripcion=f"Creación del conductor ID {resultado}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Conductor creado correctamente",
            "id_wialon": resultado
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Error inesperado al crear un conductor en Wialon"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible confirmar la creación del conductor en Wialon"
        )


@router.put("/{driver_id}")
async def actualizar_conductor(
    driver_id: int,
    datos: DriverUpdate,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles("Administrador", "Operador"))
):
    try:
        resultado = await driver_service.actualizar_conductor(
            driver_id=driver_id,
            nombre=datos.name,
            codigo=datos.code,
            telefono=datos.phone,
            descripcion=datos.description
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="UPDATE",
            modulo="CONDUCTORES",
            descripcion=f"Actualización del conductor ID {driver_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Conductor actualizado correctamente",
            "id_wialon": resultado
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Error inesperado al actualizar un conductor en Wialon"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible confirmar la actualización del conductor en Wialon"
        )


@router.delete("/{driver_id}")
async def eliminar_conductor(
    driver_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(require_roles("Administrador", "Operador"))
):
    try:
        resultado = await driver_service.eliminar_conductor(
            driver_id=driver_id
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="DELETE",
            modulo="CONDUCTORES",
            descripcion=f"Eliminación del conductor ID {driver_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Conductor eliminado correctamente",
            "id_wialon": resultado
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Error inesperado al eliminar un conductor en Wialon"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible confirmar la eliminación del conductor en Wialon"
        )
