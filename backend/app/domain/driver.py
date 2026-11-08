from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Driver:
    id: int
    name: str
    code: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    assigned_unit_id: Optional[int] = None
    custom_fields: dict[str, str] = field(default_factory=dict)