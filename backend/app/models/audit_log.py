
from datetime import datetime, timezone

from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )

    accion: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    modulo: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    descripcion: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    resultado: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    direccion_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True
    )

    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    usuario = relationship("User")
