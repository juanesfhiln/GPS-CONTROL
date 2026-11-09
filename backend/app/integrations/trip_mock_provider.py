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
                "ruta": [
                    (4.6097, -74.0817, 0, 0),
                    (4.6160, -74.0785, 480, 25.0),
                    (4.6225, -74.0750, 900, 32.0),
                    (4.6290, -74.0710, 1380, 38.0),
                    (4.6355, -74.0670, 1860, 42.0),
                    (4.6420, -74.0645, 2220, 30.0),
                    (4.6486, -74.0636, 2400, 0)
                ]
            },
            {
                "id": f"sim-{unit_id}-002",
                "inicio": time_to - 3600 * 8,
                "duracion": 3300,
                "distancia": 18.7,
                "velocidad_promedio": 34.0,
                "velocidad_maxima": 65.0,
                "ruta": [
                    (4.6486, -74.0636, 0, 0),
                    (4.6530, -74.0615, 550, 28.0),
                    (4.6580, -74.0590, 1100, 42.0),
                    (4.6630, -74.0565, 1650, 65.0),
                    (4.6680, -74.0540, 2200, 39.0),
                    (4.6730, -74.0520, 2750, 31.0),
                    (4.6784, -74.0501, 3300, 0)
                ]
            },
            {
                "id": f"sim-{unit_id}-003",
                "inicio": time_to - 3600 * 15,
                "duracion": 2100,
                "distancia": 9.3,
                "velocidad_promedio": 28.5,
                "velocidad_maxima": 52.0,
                "ruta": [
                    (4.6784, -74.0501, 0, 0),
                    (4.6670, -74.0550, 350, 24.0),
                    (4.6550, -74.0610, 700, 35.0),
                    (4.6440, -74.0680, 1050, 52.0),
                    (4.6320, -74.0730, 1400, 29.0),
                    (4.6200, -74.0780, 1750, 25.0),
                    (4.6097, -74.0817, 2100, 0)
                ]
            }
        ]

        viajes = []

        for viaje in viajes_base:
            inicio = viaje["inicio"]
            fin = inicio + viaje["duracion"]

            if inicio < time_from or fin > time_to:
                continue

            route_points = [
                {
                    "elapsed_seconds": tiempo,
                    "latitude": latitud,
                    "longitude": longitud,
                    "speed": velocidad
                }
                for latitud, longitud, tiempo, velocidad in viaje["ruta"]
            ]

            viajes.append({
                "id": viaje["id"],
                "vehicle_id": unit_id,
                "start_time": datetime.fromtimestamp(
                    inicio,
                    tz=timezone.utc
                ),
                "end_time": datetime.fromtimestamp(
                    fin,
                    tz=timezone.utc
                ),
                "duration_seconds": viaje["duracion"],
                "distance_km": viaje["distancia"],
                "start_latitude": viaje["ruta"][0][0],
                "start_longitude": viaje["ruta"][0][1],
                "end_latitude": viaje["ruta"][-1][0],
                "end_longitude": viaje["ruta"][-1][1],
                "average_speed": viaje["velocidad_promedio"],
                "max_speed": viaje["velocidad_maxima"],
                "route_points": route_points,
                "simulated": True
            })

        return viajes