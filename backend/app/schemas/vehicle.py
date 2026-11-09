from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    latitude: Optional[float]
    longitude: Optional[float]
    speed: float
    heading: Optional[int]
    heading_cardinal: Optional[str]
    altitude: Optional[float]
    position_time: Optional[datetime]
    last_message_time: Optional[datetime]
    status: str
    custom_fields: dict[str, Any] = Field(default_factory=dict)

class VehicleCustomFieldUpdate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    valor: str

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError("El nombre del campo no puede estar vacío")

        return valor