
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request

from app.api.dependencies import require_roles
from app.services.passenger_service import passenger_service
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.services.audit_service import audit_service
from app.schemas.passenger import PassengerResponse, PassengerCreate, PassengerUpdate, PassengerOperationResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/passengers",
    tags=["Pasajeros"]
)


@router.get("/", response_model=dict)
async def listar_pasajeros(
    buscar: str | None = Query(default=None, min_length=1),
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
        pasajeros = await passenger_service.obtener_pasajeros()

        if buscar is not None:
            termino = buscar.strip().lower()

            if not termino:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El término de búsqueda no puede estar vacío"
                )

            pasajeros = [
                pasajero
                for pasajero in pasajeros
                if termino in pasajero.name.lower()
                or termino in (pasajero.code or "").lower()
                or termino in (pasajero.phone or "").lower()
            ]

        total = len(pasajeros)
        inicio = (pagina - 1) * limite
        fin = inicio + limite

        resultados = pasajeros[inicio:fin]

        return {
            "total": total,
            "pagina": pagina,
            "limite": limite,
            "total_paginas": (total + limite - 1) // limite,
            "resultados": [
                PassengerResponse.model_validate(pasajero)
                for pasajero in resultados
            ]
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Error al consultar los pasajeros en Wialon"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible consultar los pasajeros en Wialon"
        )

@router.post("/", response_model=PassengerOperationResponse, status_code=status.HTTP_201_CREATED)
async def crear_pasajero(
    datos: PassengerCreate,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(
        require_roles("Administrador", "Operador")
    )
):
    try:
        pasajero_id = await passenger_service.crear_pasajero(
            nombre=datos.name,
            codigo=datos.code,
            telefono=datos.phone,
            campos_personalizados=datos.custom_fields
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="CREATE",
            modulo="PASAJEROS",
            descripcion=f"Creación del pasajero ID {pasajero_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Pasajero creado correctamente",
            "id_wialon": pasajero_id
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Error inesperado al crear un pasajero en Wialon"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible confirmar la creación del pasajero en Wialon"
        )


@router.put("/{passenger_id}", response_model=PassengerOperationResponse)

async def actualizar_pasajero(
    passenger_id: int,
    datos: PassengerUpdate,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(
        require_roles("Administrador", "Operador")
    )
):
    try:
        resultado = await passenger_service.actualizar_pasajero(
            passenger_id=passenger_id,
            nombre=datos.name,
            codigo=datos.code,
            telefono=datos.phone,
            campos_personalizados=datos.custom_fields
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="UPDATE",
            modulo="PASAJEROS",
            descripcion=f"Actualización del pasajero ID {passenger_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Pasajero actualizado correctamente",
            "id_wialon": resultado
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Error inesperado al actualizar un pasajero en Wialon"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible confirmar la actualización del pasajero en Wialon"
        )

@router.delete("/{passenger_id}", response_model=PassengerOperationResponse)
async def eliminar_pasajero(
    passenger_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(
        require_roles("Administrador", "Operador")
    )
):
    try:
        resultado = await passenger_service.eliminar_pasajero(
            passenger_id=passenger_id
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="DELETE",
            modulo="PASAJEROS",
            descripcion=f"Eliminación del pasajero ID {passenger_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Pasajero eliminado correctamente",
            "passenger_id": resultado
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Error inesperado al eliminar un pasajero en Wialon"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible confirmar la eliminación del pasajero en Wialon"
        )

@router.post("/{passenger_id}/asignar/{unit_id}", response_model=PassengerOperationResponse)
async def asignar_pasajero(
    passenger_id: int,
    unit_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(
        require_roles("Administrador", "Operador")
    )
):
    try:
        await passenger_service.asignar_pasajero(
            passenger_id=passenger_id,
            unit_id=unit_id
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="ASSIGN",
            modulo="PASAJEROS",
            descripcion=f"Asignación del pasajero ID {passenger_id} al vehículo ID {unit_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Pasajero asignado correctamente",
            "passenger_id": passenger_id,
            "unit_id": unit_id
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Error inesperado al asignar un pasajero"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible asignar el pasajero en Wialon"
        )

@router.delete("/{passenger_id}/desvincular/{unit_id}", response_model=PassengerOperationResponse)
async def desvincular_pasajero(
    passenger_id: int,
    unit_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(
        require_roles("Administrador", "Operador")
    )
):
    try:
        await passenger_service.desvincular_pasajero(
            passenger_id=passenger_id,
            unit_id=unit_id
        )

        audit_service.registrar(
            db=db,
            usuario_id=usuario.id,
            accion="UNASSIGN",
            modulo="PASAJEROS",
            descripcion=f"Desvinculación del pasajero ID {passenger_id} del vehículo ID {unit_id}",
            resultado="EXITOSO",
            direccion_ip=request.client.host if request.client else None
        )

        return {
            "mensaje": "Pasajero desvinculado correctamente",
            "passenger_id": passenger_id,
            "unit_id": unit_id
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )

    except Exception:
        logger.exception(
            "Error inesperado al desvincular un pasajero"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No fue posible desvincular el pasajero en Wialon"
        )

