
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    vehicle_id: int
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    distance_km: float
    start_latitude: float
    start_longitude: float
    end_latitude: float
    end_longitude: float
    average_speed: float
    max_speed: float
    simulated: bool = True


class TripHistoryResponse(BaseModel):
    vehicle_id: int
    vehicle_name: str
    fecha_inicio: datetime
    fecha_fin: datetime
    total_viajes: int
    viajes: list[TripResponse]
    simulated: bool = True
