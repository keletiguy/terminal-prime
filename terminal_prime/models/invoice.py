from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class InvoiceStatus(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    PAYEE = "PAYEE"
    PARTIELLE = "PARTIELLE"


@dataclass
class Invoice:
    number: str
    client_id: int
    affiliate_id: int
    date: date
    due_date: date
    amount: int
    status: InvoiceStatus
    id: Optional[int] = None
    total_paid: int = 0
    client_name: Optional[str] = None
    affiliate_name: Optional[str] = None

    @property
    def remaining(self) -> int:
        return self.amount - self.total_paid

    def is_overdue(self, today: Optional[date] = None) -> bool:
        today = today or date.today()
        return self.status != InvoiceStatus.PAYEE and self.due_date < today

    def display_status(self, today: Optional[date] = None) -> str:
        if self.is_overdue(today):
            return "EN_RETARD"
        return self.status.value

    def format_amount(self) -> str:
        return f"{self.amount:,.0f} FCFA".replace(",", " ")
