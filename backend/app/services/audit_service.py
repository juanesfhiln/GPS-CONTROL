
import logging

from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:

    @staticmethod
    def registrar(
        db: Session,
        usuario_id: int | None,
        accion: str,
        modulo: str,
        descripcion: str,
        resultado: str,
        direccion_ip: str | None = None
    ) -> AuditLog | None:
        try:
            registro = AuditLog(
                usuario_id=usuario_id,
                accion=accion,
                modulo=modulo,
                descripcion=descripcion,
                resultado=resultado,
                direccion_ip=direccion_ip
            )

            db.add(registro)
            db.commit()
            db.refresh(registro)

            return registro

        except Exception:
            db.rollback()
            logger.exception("No fue posible guardar el registro de auditoría")
            return None

    @staticmethod
    def listar(
        db: Session,
        pagina: int = 1,
        limite: int = 20,
        usuario_id: int | None = None,
        modulo: str | None = None,
        resultado: str | None = None
    ) -> list[AuditLog]:
        consulta = select(AuditLog)

        if usuario_id is not None:
            consulta = consulta.where(AuditLog.usuario_id == usuario_id)

        if modulo:
            consulta = consulta.where(AuditLog.modulo == modulo)

        if resultado:
            consulta = consulta.where(AuditLog.resultado == resultado)

        consulta = consulta.order_by(
            desc(AuditLog.fecha),
            desc(AuditLog.id)
        ).offset((pagina - 1) * limite).limit(limite)

        return list(db.scalars(consulta).all())


    @staticmethod
    def contar(
        db: Session,
        usuario_id: int | None = None,
        modulo: str | None = None,
        resultado: str | None = None
    ) -> int:
        consulta = select(func.count()).select_from(AuditLog)

        if usuario_id is not None:
            consulta = consulta.where(AuditLog.usuario_id == usuario_id)

        if modulo:
            consulta = consulta.where(AuditLog.modulo == modulo)

        if resultado:
            consulta = consulta.where(AuditLog.resultado == resultado)

        return db.scalar(consulta) or 0



audit_service = AuditService()
