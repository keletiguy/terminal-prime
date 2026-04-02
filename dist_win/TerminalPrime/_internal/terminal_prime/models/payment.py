from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class PaymentMode(str, Enum):
    VIREMENT = "VIREMENT"
    CHEQUE = "CHEQUE"
    ESPECES = "ESPECES"


@dataclass
class Payment:
    invoice_id: int
    client_id: int
    date: date
    amount: int
    mode: PaymentMode
    reference: str
    id: Optional[int] = None
