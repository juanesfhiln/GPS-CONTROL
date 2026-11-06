
from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    correo: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    cambiar_password: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    version_token: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    rol_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False
    )

    rol = relationship("Role", back_populates="usuarios")
