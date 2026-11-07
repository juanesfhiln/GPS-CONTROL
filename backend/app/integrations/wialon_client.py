
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
