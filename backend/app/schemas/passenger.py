
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PassengerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str | None = None
    phone: str | None = None
    assigned_unit_id: int | None = None
    custom_fields: dict[str, str] = Field(default_factory=dict)


class PassengerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(default="", max_length=50)
    phone: str = Field(default="", max_length=30)
    custom_fields: dict[str, str] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre del pasajero es obligatorio")

        return valor


class PassengerUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(default="", max_length=50)
    phone: str = Field(default="", max_length=30)
    custom_fields: dict[str, str] | None = None

    @field_validator("name")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre del pasajero es obligatorio")

        return valor


class PassengerOperationResponse(BaseModel):
    mensaje: str
    id_wialon: int | None = None
    passenger_id: int | None = None
    unit_id: int | None = None
