from dataclasses import dataclass
from typing import Optional


@dataclass
class Client:
    name: str
    id: Optional[int] = None
    contact_email: Optional[str] = None
