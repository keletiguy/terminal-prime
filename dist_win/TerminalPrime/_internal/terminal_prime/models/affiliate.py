from dataclasses import dataclass
from typing import Optional


@dataclass
class Affiliate:
    name: str
    client_id: int
    id: Optional[int] = None
