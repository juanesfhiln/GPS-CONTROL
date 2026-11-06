from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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