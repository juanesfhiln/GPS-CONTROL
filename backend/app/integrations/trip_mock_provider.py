
from datetime import datetime, timezone


class TripMockProvider:

    async def get_trips(
        self,
        unit_id: int,
        time_from: int,
        time_to: int
    ) -> list[dict]:

        if unit_id <= 0:
            raise ValueError("El ID del vehículo no es válido")

        if time_from <= 0 or time_to <= time_from:
            raise ValueError("El intervalo de fechas no es válido")

        viajes_base = [
            {
                "id": f"sim-{unit_id}-001",
                "inicio": time_to - 3600 * 3,
                "duracion": 2400,
                "distancia": 12.5,
                "velocidad_promedio": 31.2,
                "velocidad_maxima": 58.0,
                "inicio_lat": 4.6097,
                "inicio_lon": -74.0817,
                "fin_lat": 4.6486,
                "fin_lon": -74.0636
            },
            {
                "id": f"sim-{unit_id}-002",
                "inicio": time_to - 3600 * 8,
                "duracion": 3300,
                "distancia": 18.7,
                "velocidad_promedio": 34.0,
                "velocidad_maxima": 65.0,
                "inicio_lat": 4.6486,
                "inicio_lon": -74.0636,
                "fin_lat": 4.6784,
                "fin_lon": -74.0501
            },
            {
                "id": f"sim-{unit_id}-003",
                "inicio": time_to - 3600 * 15,
                "duracion": 2100,
                "distancia": 9.3,
                "velocidad_promedio": 28.5,
                "velocidad_maxima": 52.0,
                "inicio_lat": 4.6784,
                "inicio_lon": -74.0501,
                "fin_lat": 4.6097,
                "fin_lon": -74.0817
            }
        ]

        viajes = []

        for viaje in viajes_base:
            inicio = viaje["inicio"]
            fin = inicio + viaje["duracion"]

            if inicio < time_from or fin > time_to:
                continue

            viajes.append({
                "id": viaje["id"],
                "vehicle_id": unit_id,
                "start_time": datetime.fromtimestamp(
                    inicio, tz=timezone.utc
                ),
                "end_time": datetime.fromtimestamp(
                    fin, tz=timezone.utc
                ),
                "duration_seconds": viaje["duracion"],
                "distance_km": viaje["distancia"],
                "start_latitude": viaje["inicio_lat"],
                "start_longitude": viaje["inicio_lon"],
                "end_latitude": viaje["fin_lat"],
                "end_longitude": viaje["fin_lon"],
                "average_speed": viaje["velocidad_promedio"],
                "max_speed": viaje["velocidad_maxima"],
                "simulated": True
            })

        return viajes
