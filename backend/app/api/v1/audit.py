
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.db.dependencies import get_db
from app.schemas.audit import AuditListResponse
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/", response_model=AuditListResponse)
def listar_registros_auditoria(
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=20, ge=1, le=100),
    usuario_id: int | None = Query(default=None, ge=1),
    modulo: str | None = Query(default=None),
    resultado: str | None = Query(default=None),
    db: Session = Depends(get_db),
    usuario=Depends(require_roles("Administrador"))
):
    total = audit_service.contar(
        db=db,
        usuario_id=usuario_id,
        modulo=modulo,
        resultado=resultado
    )

    resultados = audit_service.listar(
        db=db,
        pagina=pagina,
        limite=limite,
        usuario_id=usuario_id,
        modulo=modulo,
        resultado=resultado
    )

    return {
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": (total + limite - 1) // limite,
        "resultados": resultados
    }
