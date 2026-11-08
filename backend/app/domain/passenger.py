
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Passenger:
    id: int
    name: str
    code: Optional[str] = None
    phone: Optional[str] = None
    assigned_unit_id: Optional[int] = None
    custom_fields: dict[str, str] = field(default_factory=dict)
