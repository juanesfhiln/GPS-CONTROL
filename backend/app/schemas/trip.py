from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TripRoutePoint(BaseModel):
    elapsed_seconds: int = Field(ge=0)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed: float = Field(ge=0)


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
    route_points: list[TripRoutePoint]
    simulated: bool = False


class TripHistoryResponse(BaseModel):
    vehicle_id: int
    vehicle_name: str
    fecha_inicio: datetime
    fecha_fin: datetime
    total_viajes: int
    viajes: list[TripResponse]
    simulated: bool = True