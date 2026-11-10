from datetime import datetime, timezone
import math

from app.integrations.wialon_client import WialonClient
from app.services.vehicle_service import vehicle_service


class TripService:

    def __init__(self, wialon_client=None):
        # Reutiliza el cliente que inicializa y cierra el lifespan de FastAPI.
        self.wialon_client = (
            wialon_client if wialon_client is not None
            else vehicle_service.wialon_client
        )

    @staticmethod
    def _obtener_coordenada(mensaje):
        posicion = mensaje.get("pos") or {}
        if not isinstance(posicion, dict):
            return None

        try:
            latitud = float(posicion.get("y"))
            longitud = float(posicion.get("x"))
            velocidad = max(0.0, float(posicion.get("s", 0) or 0))
            timestamp = int(mensaje.get("t"))
        except (TypeError, ValueError, OverflowError):
            return None

        if (
            not math.isfinite(latitud)
            or not math.isfinite(longitud)
            or not -90 <= latitud <= 90
            or not -180 <= longitud <= 180
        ):
            return None

        return {
            "timestamp": timestamp,
            "latitude": latitud,
            "longitude": longitud,
            "speed": velocidad
        }

    @classmethod
    def _construir_puntos_ruta(cls, mensajes, viaje, inicio, fin):
        desde = viaje.get("from") or {}
        hasta = viaje.get("to") or {}

        try:
            indice_inicio = int(desde.get("i"))
            indice_fin = int(hasta.get("i"))
        except (TypeError, ValueError):
            indice_inicio = indice_fin = -1

        candidatos = []
        if 0 <= indice_inicio <= indice_fin < len(mensajes):
            candidatos = mensajes[indice_inicio:indice_fin + 1]

        # Si los índices no son utilizables, se filtra por tiempo. Esto evita
        # perder la geometría si la respuesta no conserva índices contiguos.
        if not candidatos:
            candidatos = [
                mensaje for mensaje in mensajes
                if isinstance(mensaje, dict)
                and inicio <= int(mensaje.get("t", -1) or -1) <= fin
            ]

        puntos = []
        for mensaje in candidatos:
            if not isinstance(mensaje, dict):
                continue
            punto = cls._obtener_coordenada(mensaje)
            if punto is None or not inicio <= punto["timestamp"] <= fin:
                continue
            puntos.append({
                "elapsed_seconds": max(0, punto["timestamp"] - inicio),
                "latitude": punto["latitude"],
                "longitude": punto["longitude"],
                "speed": punto["speed"]
            })

        puntos.sort(key=lambda punto: punto["elapsed_seconds"])

        # Garantiza los extremos del viaje si no aparecen en los mensajes.
        for extremo, tiempo in ((desde, inicio), (hasta, fin)):
            ubicacion = extremo.get("p") or {}
            try:
                latitud = float(ubicacion.get("y"))
                longitud = float(ubicacion.get("x"))
            except (TypeError, ValueError):
                continue
            if not (-90 <= latitud <= 90 and -180 <= longitud <= 180):
                continue
            if not any(
                punto["elapsed_seconds"] == tiempo - inicio
                and abs(punto["latitude"] - latitud) < 0.000001
                and abs(punto["longitude"] - longitud) < 0.000001
                for punto in puntos
            ):
                puntos.append({
                    "elapsed_seconds": max(0, tiempo - inicio),
                    "latitude": latitud,
                    "longitude": longitud,
                    "speed": 0.0
                })

        puntos.sort(key=lambda punto: punto["elapsed_seconds"])
        return puntos

    async def obtener_historial(
        self,
        unidad_id: int,
        fecha_inicio: datetime,
        fecha_fin: datetime
    ) -> dict:
        if isinstance(unidad_id, bool) or not isinstance(unidad_id, int) or unidad_id <= 0:
            raise ValueError("El ID del vehículo no es válido")

        if fecha_inicio >= fecha_fin:
            raise ValueError("La fecha inicial debe ser anterior a la fecha final")

        if fecha_inicio.tzinfo is None:
            fecha_inicio = fecha_inicio.replace(tzinfo=timezone.utc)
        else:
            fecha_inicio = fecha_inicio.astimezone(timezone.utc)

        if fecha_fin.tzinfo is None:
            fecha_fin = fecha_fin.replace(tzinfo=timezone.utc)
        else:
            fecha_fin = fecha_fin.astimezone(timezone.utc)

        vehiculos = await vehicle_service.obtener_vehiculos()
        vehiculo = next((v for v in vehiculos if v.id == unidad_id), None)

        if vehiculo is None:
            raise ValueError("El vehículo solicitado no existe")

        datos = await self.wialon_client.get_unit_trips(
            unidad_id,
            int(fecha_inicio.timestamp()),
            int(fecha_fin.timestamp())
        )

        viajes_wialon = datos.get("trips", [])
        mensajes = datos.get("messages", [])

        viajes = []
        for indice, viaje in enumerate(viajes_wialon):
            desde = viaje.get("from") or {}
            hasta = viaje.get("to") or {}

            try:
                inicio = int(desde["t"])
                fin = int(hasta["t"])
                distancia_metros = float(viaje.get("m", 0) or 0)
            except (KeyError, TypeError, ValueError, OverflowError):
                continue

            if fin <= inicio or not math.isfinite(distancia_metros):
                continue

            puntos = self._construir_puntos_ruta(
                mensajes, viaje, inicio, fin
            )

            ubicacion_inicio = desde.get("p") or {}
            ubicacion_fin = hasta.get("p") or {}
            if not puntos:
                continue

            duracion = fin - inicio
            distancia_km = max(0.0, distancia_metros / 1000)
            velocidades = [punto["speed"] for punto in puntos]
            velocidad_promedio = (
                distancia_km / (duracion / 3600)
                if duracion > 0 else 0.0
            )

            primer_punto = puntos[0]
            ultimo_punto = puntos[-1]

            viajes.append({
                "id": f"wialon-{unidad_id}-{inicio}-{indice}",
                "vehicle_id": unidad_id,
                "start_time": datetime.fromtimestamp(inicio, tz=timezone.utc),
                "end_time": datetime.fromtimestamp(fin, tz=timezone.utc),
                "duration_seconds": duracion,
                "distance_km": round(distancia_km, 3),
                "start_latitude": float(ubicacion_inicio.get("y", primer_punto["latitude"])),
                "start_longitude": float(ubicacion_inicio.get("x", primer_punto["longitude"])),
                "end_latitude": float(ubicacion_fin.get("y", ultimo_punto["latitude"])),
                "end_longitude": float(ubicacion_fin.get("x", ultimo_punto["longitude"])),
                "average_speed": round(velocidad_promedio, 2),
                "max_speed": round(max(velocidades, default=0.0), 2),
                "route_points": puntos,
                "simulated": False
            })

        return {
            "vehicle_id": vehiculo.id,
            "vehicle_name": vehiculo.name,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "total_viajes": len(viajes),
            "viajes": viajes,
            "simulated": False
        }


trip_service = TripService()
