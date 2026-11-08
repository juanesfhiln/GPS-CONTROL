
import os
import json
import asyncio
import httpx

from dotenv import load_dotenv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class WialonClient:

    def __init__(self):
        self.api_url = os.getenv("WIALON_API_URL")
        self.token = os.getenv("WIALON_TOKEN")

        self.session_id = None
        self._session_lock = asyncio.Lock()
        self._http_client = None

        if not self.api_url or not self.token:
            raise RuntimeError("Faltan las credenciales de Wialon")

    async def iniciar(self):
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=20)

    async def cerrar(self):
        if self._http_client is not None and not self._http_client.is_closed:
            await self._http_client.aclose()

        self._http_client = None

    async def login(self):
        async with self._session_lock:

            if self.session_id:
                return True

            params = {
                "svc": "token/login",
                "params": json.dumps({
                    "token": self.token
                })
            }

            response = await self._http_client.get(
                self.api_url,
                params=params
            )
            response.raise_for_status()
            data = response.json()

            if "eid" not in data:
                raise RuntimeError(
                    "Wialon no devolvió un identificador de sesión"
                )

            self.session_id = data["eid"]

            return True

    async def _consultar(self, servicio, parametros):

        await self.login()

        for intento in range(2):

            params = {
                "svc": servicio,
                "params": json.dumps(parametros),
                "sid": self.session_id
            }

            response = await self._http_client.get(
                self.api_url,
                params=params
            )
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict):

                if data.get("error") == 1 and intento == 0:
                    sesion_anterior = self.session_id
                    await self._renovar_sesion(sesion_anterior)
                    continue

                if "error" in data:
                    raise RuntimeError(
                        f"Error de Wialon en {servicio}: "
                        f"código {data['error']}"
                    )

            return data

        raise RuntimeError(
            "No fue posible recuperar la sesión de Wialon"
        )

    async def _renovar_sesion(self, sesion_anterior):
        async with self._session_lock:

            if self.session_id != sesion_anterior:
                return

            self.session_id = None

            params = {
                "svc": "token/login",
                "params": json.dumps({
                    "token": self.token
                })
            }

            response = await self._http_client.get(
                self.api_url,
                params=params
            )
            response.raise_for_status()
            data = response.json()

            if "eid" not in data:
                raise RuntimeError(
                    "Wialon no devolvió un identificador de sesión"
                )

            self.session_id = data["eid"]

    async def get_units(self):

        request_params = {
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_name",
                "propValueMask": "*",
                "sortType": "sys_name"
            },
            "force": 1,
            "flags": 1025,
            "from": 0,
            "to": 0
        }

        data = await self._consultar(
            "core/search_items",
            request_params
        )

        return data.get("items", [])

    async def get_resources(self):
        request_params = {
            "spec": {
                "itemsType": "avl_resource",
                "propName": "sys_name",
                "propValueMask": "*",
                "sortType": "sys_name"
            },
            "force": 1,
            "flags": 2097409,
            "from": 0,
            "to": 0
        }

        data = await self._consultar(
            "core/search_items",
            request_params
        )

        return data.get("items", [])

    async def get_unit_drivers(self, unit_id: int):
        if unit_id <= 0:
            raise ValueError("El ID del vehículo no es válido")

        params = {
            "unitId": unit_id
        }

        return await self._consultar(
            "resource/get_unit_drivers",
            params
        )

    async def get_driver_bindings(
        self,
        resource_id: int,
        time_from: int,
        time_to: int,
        unit_id: int = 0,
        driver_id: int = 0
    ):
        if resource_id <= 0:
            raise ValueError("El ID del recurso no es válido")

        if time_from < 0 or time_to <= time_from:
            raise ValueError("El intervalo de tiempo no es válido")

        params = {
            "resourceId": resource_id,
            "unitId": unit_id,
            "driverId": driver_id,
            "timeFrom": time_from,
            "timeTo": time_to
        }

        return await self._consultar(
            "resource/get_driver_bindings",
            params
        )

    async def bind_unit_driver(
        self,
        resource_id: int,
        unit_id: int,
        driver_id: int,
        asignar: bool = True
    ):
        if resource_id <= 0:
            raise ValueError("El ID del recurso no es válido")

        if unit_id <= 0:
            raise ValueError("El ID del vehículo no es válido")

        if driver_id <= 0:
            raise ValueError("El ID del conductor no es válido")

        params = {
            "resourceId": resource_id,
            "unitId": unit_id,
            "driverId": driver_id,
            "time": 0,
            "mode": asignar
        }

        return await self._consultar(
            "resource/bind_unit_driver",
            params
        )

    async def crear_conductor(
        self,
        resource_id: int,
        nombre: str,
        codigo: str = "",
        telefono: str = "",
        descripcion: str = ""
    ):
        nombre = nombre.strip()

        if not nombre:
            raise ValueError("El nombre del conductor es obligatorio")

        params = {
            "itemId": resource_id,
            "id": 0,
            "callMode": "create",
            "n": nombre,
            "c": codigo.strip(),
            "p": telefono.strip(),
            "ds": descripcion.strip(),
            "pwd": ""
        }

        return await self._consultar(
            "resource/update_driver",
            params
        )

    async def actualizar_conductor(
        self,
        resource_id: int,
        driver_id: int,
        nombre: str,
        codigo: str = "",
        telefono: str = "",
        descripcion: str = "",
        campos_personalizados: dict[str, str] | None = None
    ):
        nombre = nombre.strip()

        if not nombre:
            raise ValueError("El nombre del conductor es obligatorio")

        params = {
            "itemId": resource_id,
            "id": driver_id,
            "callMode": "update",
            "n": nombre,
            "c": codigo.strip(),
            "p": telefono.strip(),
            "ds": descripcion.strip(),
            "jp": campos_personalizados or {}
        }

        return await self._consultar(
            "resource/update_driver",
            params
        )

    async def eliminar_conductor(
        self,
        resource_id: int,
        driver_id: int
    ):
        if driver_id <= 0:
            raise ValueError("El ID del conductor no es válido")

        params = {
            "itemId": resource_id,
            "id": driver_id,
            "callMode": "delete"
        }

        return await self._consultar(
            "resource/update_driver",
            params
        )

    async def actualizar_pasajero(
        self,
        resource_id: int,
        tag_id: int,
        nombre: str = "",
        codigo: str = "",
        telefono: str = "",
        campos_personalizados: dict[str, str] | None = None,
        call_mode: str = "create"
    ):
        if resource_id <= 0:
            raise ValueError("El ID del recurso no es válido")

        if call_mode not in ("create", "update", "delete"):
            raise ValueError("La operación del pasajero no es válida")

        if call_mode == "delete":
            if tag_id <= 0:
                raise ValueError("El ID del pasajero no es válido")

        else:
            nombre = nombre.strip()
            codigo = codigo.strip()
            telefono = telefono.strip()

            if not nombre:
                raise ValueError("El nombre del pasajero es obligatorio")

            if call_mode == "update" and tag_id <= 0:
                raise ValueError("El ID del pasajero no es válido")

            if call_mode == "create" and tag_id != 0:
                raise ValueError("Para crear un pasajero, el ID debe ser 0")

            if campos_personalizados is None:
                raise ValueError(
                    "Debes proporcionar los campos personalizados"
                )

            if not isinstance(campos_personalizados, dict):
                raise ValueError(
                    "Los campos personalizados deben ser un diccionario"
                )

            if any(
                not isinstance(clave, str)
                or not clave.strip()
                or not isinstance(valor, str)
                for clave, valor in campos_personalizados.items()
            ):
                raise ValueError(
                    "Los campos personalizados deben contener claves y valores de texto válidos"
                )

        params = {
            "itemId": resource_id,
            "id": tag_id,
            "callMode": call_mode
        }

        if call_mode != "delete":
            params.update({
                "n": nombre,
                "c": codigo,
                "p": telefono,
                "tz": 0,
                "jp": campos_personalizados
            })

        return await self._consultar(
            "resource/update_tag",
            params
        )

    async def vincular_pasajero(
        self,
        resource_id: int,
        unit_id: int,
        tag_id: int,
        asignar: bool = True
    ):
        if resource_id <= 0:
            raise ValueError("El ID del recurso no es válido")

        if unit_id <= 0:
            raise ValueError("El ID del vehículo no es válido")

        if tag_id <= 0:
            raise ValueError("El ID del pasajero no es válido")

        params = {
            "resourceId": resource_id,
            "unitId": unit_id,
            "tagId": tag_id,
            "time": 0,
            "mode": asignar
        }

        return await self._consultar(
            "resource/bind_unit_tag",
            params
        )

    async def get_tag_bindings(
        self,
        resource_id: int,
        time_from: int,
        time_to: int,
        unit_id: int = 0,
        tag_id: int = 0
    ):
        if resource_id <= 0:
            raise ValueError("El ID del recurso no es válido")

        if time_from < 0 or time_to <= time_from:
            raise ValueError("El intervalo de tiempo no es válido")

        params = {
            "resourceId": resource_id,
            "unitId": unit_id,
            "tagId": tag_id,
            "timeFrom": time_from,
            "timeTo": time_to
        }

        return await self._consultar(
            "resource/get_tag_bindings",
            params
        )
