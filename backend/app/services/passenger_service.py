
import os
import logging

from app.services.vehicle_service import vehicle_service
from app.integrations.wialon_mapper import convertir_pasajero
from app.domain.passenger import Passenger

logger = logging.getLogger(__name__)


class PassengerService:

    def __init__(self, wialon_client):
        self.wialon_client = wialon_client
        self.resource_id = int(
            os.getenv("WIALON_RESOURCE_ID", "27668776")
        )

    async def obtener_pasajeros(self) -> list[Passenger]:

        recursos = await self.wialon_client.get_resources()

        recurso = next(
            (
                r for r in recursos
                if r.get("id") == self.resource_id
            ),
            None
        )

        if recurso is None:
            raise RuntimeError(
                "No se encontró el recurso configurado en Wialon"
            )

        pasajeros = recurso.get("tags", {})

        if not isinstance(pasajeros, dict):
            raise RuntimeError(
                "Wialon devolvió una estructura inesperada de etiquetas"
            )

        return [
            convertir_pasajero(datos)
            for datos in pasajeros.values()
        ]

    async def crear_pasajero(
        self,
        nombre: str,
        codigo: str = "",
        telefono: str = "",
        campos_personalizados: dict[str, str] | None = None
    ):
        nombre = nombre.strip()
        codigo = codigo.strip()
        telefono = telefono.strip()

        if not nombre:
            raise ValueError("El nombre del pasajero es obligatorio")

        if not isinstance(campos_personalizados or {}, dict):
            raise ValueError("Los campos personalizados deben ser un diccionario")

        if "_telefono" in (campos_personalizados or {}):
            raise ValueError(
                "La clave _telefono está reservada para uso interno"
            )

        if any(
            not isinstance(clave, str)
            or not clave.strip()
            or not isinstance(valor, str)
            for clave, valor in (campos_personalizados or {}).items()
        ):
            raise ValueError(
                "Los campos personalizados deben contener claves y valores de texto válidos"
            )

        pasajeros = await self.obtener_pasajeros()

        if codigo and any(
            pasajero.code
            and pasajero.code.strip().lower() == codigo.lower()
            for pasajero in pasajeros
        ):
            raise ValueError("Ya existe un pasajero con ese código")

        if telefono and any(
            pasajero.phone
            and pasajero.phone.strip() == telefono
            for pasajero in pasajeros
        ):
            raise ValueError("Ya existe un pasajero con ese teléfono")

        campos_finales = dict(campos_personalizados or {})

        if telefono:
            campos_finales["_telefono"] = telefono

        resultado = await self.wialon_client.actualizar_pasajero(
            resource_id=self.resource_id,
            tag_id=0,
            nombre=nombre,
            codigo=codigo,
            telefono=telefono,
            campos_personalizados=campos_finales,
            call_mode="create"
        )

        if (
            not isinstance(resultado, list)
            or len(resultado) != 2
            or not isinstance(resultado[0], int)
            or isinstance(resultado[0], bool)
            or resultado[0] <= 0
            or not isinstance(resultado[1], dict)
        ):
            raise RuntimeError(
                "Wialon devolvió una respuesta inesperada al crear el pasajero"
            )

        return resultado[0]

    async def actualizar_pasajero(
        self,
        passenger_id: int,
        nombre: str,
        codigo: str = "",
        telefono: str | None = None,
        campos_personalizados: dict[str, str] | None = None
    ):
        if passenger_id <= 0:
            raise ValueError("El ID del pasajero no es válido")

        nombre = nombre.strip()
        codigo = codigo.strip()

        if telefono is not None:
            telefono = telefono.strip()

        if not nombre:
            raise ValueError("El nombre del pasajero es obligatorio")

        if campos_personalizados is not None:
            if not isinstance(campos_personalizados, dict):
                raise ValueError("Los campos personalizados deben ser un diccionario")

            if "_telefono" in campos_personalizados:
                raise ValueError(
                    "La clave _telefono está reservada para uso interno"
                )

            if any(
                not isinstance(clave, str)
                or not isinstance(valor, str)
                or not clave.strip()
                for clave, valor in campos_personalizados.items()
            ):
                raise ValueError(
                    "Los campos personalizados deben tener claves y valores de texto válidos"
                )

        pasajeros = await self.obtener_pasajeros()

        pasajero_actual = next(
            (
                pasajero
                for pasajero in pasajeros
                if pasajero.id == passenger_id
            ),
            None
        )

        if pasajero_actual is None:
            raise ValueError("No se encontró el pasajero")

        if codigo and any(
            pasajero.id != passenger_id
            and pasajero.code
            and pasajero.code.strip().lower() == codigo.lower()
            for pasajero in pasajeros
        ):
            raise ValueError("Ya existe otro pasajero con ese código")

        telefono_final = (
            pasajero_actual.phone
            if telefono is None
            else telefono
        )

        if telefono_final and any(
            pasajero.id != passenger_id
            and pasajero.phone
            and pasajero.phone.strip() == telefono_final
            for pasajero in pasajeros
        ):
            raise ValueError("Ya existe otro pasajero con ese teléfono")

        campos_finales = dict(
            campos_personalizados
            if campos_personalizados is not None
            else pasajero_actual.custom_fields
        )

        campos_finales.pop("_telefono", None)

        if telefono_final:
            campos_finales["_telefono"] = telefono_final

        resultado = await self.wialon_client.actualizar_pasajero(
            resource_id=self.resource_id,
            tag_id=passenger_id,
            nombre=nombre,
            codigo=codigo,
            telefono=telefono_final,
            campos_personalizados=campos_finales,
            call_mode="update"
        )

        if (
            not isinstance(resultado, list)
            or len(resultado) != 2
            or resultado[0] != passenger_id
            or not isinstance(resultado[1], dict)
        ):
            raise RuntimeError(
                "Wialon devolvió una respuesta inesperada al actualizar el pasajero"
            )

        return passenger_id

    async def eliminar_pasajero(self, passenger_id: int):
        if passenger_id <= 0:
            raise ValueError("El ID del pasajero no es válido")

        pasajeros = await self.obtener_pasajeros()

        pasajero = next(
            (
                pasajero
                for pasajero in pasajeros
                if pasajero.id == passenger_id
            ),
            None
        )

        if pasajero is None:
            raise ValueError("No se encontró el pasajero")

        if pasajero.assigned_unit_id is not None:
            raise ValueError(
                "No se puede eliminar un pasajero asignado a un vehículo"
            )

        resultado = await self.wialon_client.actualizar_pasajero(
            resource_id=self.resource_id,
            tag_id=passenger_id,
            call_mode="delete"
        )

        if (
            not isinstance(resultado, list)
            or len(resultado) != 2
            or resultado[0] != passenger_id
            or resultado[1] is not None
        ):
            raise RuntimeError(
                "Wialon devolvió una respuesta inesperada al eliminar el pasajero"
            )

        return passenger_id


    async def asignar_pasajero(self, passenger_id: int, unit_id: int):
        if passenger_id <= 0 or unit_id <= 0:
            raise ValueError(
                "El ID del pasajero o vehículo no es válido"
            )

        pasajeros = await self.obtener_pasajeros()

        pasajero = next(
            (p for p in pasajeros if p.id == passenger_id),
            None
        )

        if pasajero is None:
            raise ValueError("El pasajero no existe en Wialon")

        unidades = await self.wialon_client.get_units()

        if not any(u.get("id") == unit_id for u in unidades):
            raise ValueError("El vehículo no existe en Wialon")

        if pasajero.assigned_unit_id is not None:
            raise ValueError(
                "El pasajero ya está asignado a un vehículo"
            )

        return await self.wialon_client.vincular_pasajero(
            resource_id=self.resource_id,
            unit_id=unit_id,
            tag_id=passenger_id,
            asignar=True
        )


    async def desvincular_pasajero(
        self,
        passenger_id: int,
        unit_id: int
    ):
        if passenger_id <= 0 or unit_id <= 0:
            raise ValueError(
                "El ID del pasajero o vehículo no es válido"
            )

        pasajeros = await self.obtener_pasajeros()

        pasajero = next(
            (p for p in pasajeros if p.id == passenger_id),
            None
        )

        if pasajero is None:
            raise ValueError("El pasajero no existe en Wialon")

        if pasajero.assigned_unit_id != unit_id:
            raise ValueError(
                "El pasajero no está asignado a este vehículo"
            )

        return await self.wialon_client.vincular_pasajero(
            resource_id=self.resource_id,
            unit_id=unit_id,
            tag_id=passenger_id,
            asignar=False
        )



passenger_service = PassengerService(
    vehicle_service.wialon_client
)
