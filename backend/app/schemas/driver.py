from pydantic import BaseModel, ConfigDict, Field, field_validator


class DriverCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(default="", max_length=50)
    phone: str = Field(default="", max_length=30)
    description: str = Field(default="", max_length=250)

    @field_validator("name")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre del conductor es obligatorio")

        return valor


class DriverResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str | None = None
    phone: str | None = None
    description: str | None = None
    assigned_unit_id: int | None = None
    custom_fields: dict[str, str] = Field(default_factory=dict)

class DriverUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(default="", max_length=50)
    phone: str = Field(default="", max_length=30)
    description: str = Field(default="", max_length=250)

    @field_validator("name")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre del conductor es obligatorio")

        return valor