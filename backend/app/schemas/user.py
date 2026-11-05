
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    correo: EmailStr
    password: str = Field(min_length=8)
    rol_id: int


class UserUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    correo: EmailStr | None = None
    rol_id: int | None = None


class UserResponse(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    activo: bool
    cambiar_password: bool
    rol: str

    model_config = ConfigDict(from_attributes=True)
