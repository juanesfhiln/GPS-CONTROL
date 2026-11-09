from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Vehicle:
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
    communication_status: str = "sin_señal"
    position_status: str = "sin_posicion"
    custom_fields: dict[str, Any] = field(default_factory=dict)