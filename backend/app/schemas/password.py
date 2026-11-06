
from pydantic import BaseModel, Field, model_validator


class PasswordChange(BaseModel):
    password_actual: str = Field(min_length=1)
    password_nueva: str = Field(min_length=12, max_length=128)
    confirmar_password: str = Field(min_length=12, max_length=128)

    @model_validator(mode="after")
    def validar_passwords(self):
        if self.password_nueva != self.confirmar_password:
            raise ValueError("Las contraseñas nuevas no coinciden")

        if self.password_actual == self.password_nueva:
            raise ValueError(
                "La nueva contraseña debe ser diferente"
            )

        return self
