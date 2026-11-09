
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: Optional[int]
    accion: str
    modulo: str
    descripcion: str
    resultado: str
    direccion_ip: Optional[str]
    fecha: datetime


class AuditListResponse(BaseModel):
    total: int
    pagina: int
    limite: int
    total_paginas: int
    resultados: list[AuditLogResponse]
