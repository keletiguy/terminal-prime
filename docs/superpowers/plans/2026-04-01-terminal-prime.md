# Terminal Prime Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Linux desktop app for aged trade balance management in the pharmaceutical sector, importing invoices from Mediciel and tracking payments/collections.

**Architecture:** Python 3 + CustomTkinter MVC. SQLite database with 4 tables (clients, affiliates, invoices, payments). 5 screens navigated via sidebar frame stacking. Carbon Console dark theme.

**Tech Stack:** Python 3.10+, CustomTkinter, SQLite3, openpyxl, reportlab, Pillow

**Spec:** `docs/superpowers/specs/2026-04-01-terminal-prime-design.md`

---

## Chunk 1: Foundation (models, database, theme)

### Task 1: Project setup and dependencies

**Files:**
- Create: `terminal_prime/main.py`
- Create: `requirements.txt`

- [ ] **Step 1: Create project structure**

```bash
mkdir -p terminal_prime/{database,models,services,views,components}
touch terminal_prime/__init__.py
touch terminal_prime/database/__init__.py
touch terminal_prime/models/__init__.py
touch terminal_prime/services/__init__.py
touch terminal_prime/views/__init__.py
touch terminal_prime/components/__init__.py
```

- [ ] **Step 2: Create requirements.txt**

```
customtkinter>=5.2.0
openpyxl>=3.1.0
reportlab>=4.0
Pillow>=10.0
```

- [ ] **Step 3: Install dependencies**

Run: `pip install -r requirements.txt`

- [ ] **Step 4: Create main.py stub**

```python
import customtkinter as ctk
from terminal_prime.app import App


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Commit**

```bash
git init
echo "__pycache__/" > .gitignore
echo "*.db" >> .gitignore
echo ".superpowers/" >> .gitignore
git add .
git commit -m "chore: init project structure and dependencies"
```

---

### Task 2: Data models

**Files:**
- Create: `terminal_prime/models/client.py`
- Create: `terminal_prime/models/affiliate.py`
- Create: `terminal_prime/models/invoice.py`
- Create: `terminal_prime/models/payment.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write tests for models**

```python
# tests/test_models.py
from datetime import date, timedelta
from terminal_prime.models.client import Client
from terminal_prime.models.affiliate import Affiliate
from terminal_prime.models.invoice import Invoice, InvoiceStatus
from terminal_prime.models.payment import Payment, PaymentMode


def test_client_creation():
    c = Client(id=1, name="MCI CARE CI", contact_email="contact@mci.ci")
    assert c.name == "MCI CARE CI"
    assert c.id == 1


def test_affiliate_creation():
    a = Affiliate(id=1, name="SERVAIRE ABIDJAN", client_id=1)
    assert a.name == "SERVAIRE ABIDJAN"
    assert a.client_id == 1


def test_invoice_creation():
    inv = Invoice(
        id=1, number="0112-3112-2431928", client_id=1, affiliate_id=1,
        date=date(2025, 1, 1), due_date=date(2025, 1, 31),
        amount=7576, status=InvoiceStatus.EN_ATTENTE
    )
    assert inv.amount == 7576
    assert inv.status == InvoiceStatus.EN_ATTENTE


def test_invoice_is_overdue():
    inv = Invoice(
        id=1, number="TEST-001", client_id=1, affiliate_id=1,
        date=date(2024, 1, 1), due_date=date(2024, 1, 31),
        amount=10000, status=InvoiceStatus.EN_ATTENTE
    )
    assert inv.is_overdue(today=date(2024, 2, 15)) is True
    assert inv.is_overdue(today=date(2024, 1, 15)) is False


def test_invoice_paid_not_overdue():
    inv = Invoice(
        id=1, number="TEST-002", client_id=1, affiliate_id=1,
        date=date(2024, 1, 1), due_date=date(2024, 1, 31),
        amount=10000, status=InvoiceStatus.PAYEE
    )
    assert inv.is_overdue(today=date(2024, 2, 15)) is False


def test_invoice_display_status():
    inv = Invoice(
        id=1, number="TEST-003", client_id=1, affiliate_id=1,
        date=date(2024, 1, 1), due_date=date(2024, 1, 31),
        amount=10000, status=InvoiceStatus.EN_ATTENTE
    )
    assert inv.display_status(today=date(2024, 2, 15)) == "EN_RETARD"
    assert inv.display_status(today=date(2024, 1, 15)) == "EN_ATTENTE"


def test_invoice_remaining_balance():
    inv = Invoice(
        id=1, number="TEST-004", client_id=1, affiliate_id=1,
        date=date(2024, 1, 1), due_date=date(2024, 1, 31),
        amount=10000, status=InvoiceStatus.PARTIELLE,
        total_paid=6000
    )
    assert inv.remaining == 4000


def test_payment_creation():
    p = Payment(
        id=1, invoice_id=1, client_id=1,
        date=date(2025, 2, 1), amount=7576,
        mode=PaymentMode.VIREMENT, reference="PAY-00001"
    )
    assert p.amount == 7576
    assert p.mode == PaymentMode.VIREMENT


def test_format_fcfa():
    inv = Invoice(
        id=1, number="TEST-005", client_id=1, affiliate_id=1,
        date=date(2024, 1, 1), due_date=date(2024, 1, 31),
        amount=1234500, status=InvoiceStatus.EN_ATTENTE
    )
    assert inv.format_amount() == "1 234 500 FCFA"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_models.py -v`
Expected: FAIL — modules don't exist yet

- [ ] **Step 3: Implement models**

```python
# terminal_prime/models/client.py
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Client:
    name: str
    id: Optional[int] = None
    contact_email: Optional[str] = None
```

```python
# terminal_prime/models/affiliate.py
from dataclasses import dataclass
from typing import Optional


@dataclass
class Affiliate:
    name: str
    client_id: int
    id: Optional[int] = None
```

```python
# terminal_prime/models/invoice.py
from dataclasses import dataclass, field
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
```

```python
# terminal_prime/models/payment.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_models.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add terminal_prime/models/ tests/test_models.py
git commit -m "feat: add data models (Client, Affiliate, Invoice, Payment)"
```

---

### Task 3: Database connection and schema

**Files:**
- Create: `terminal_prime/database/connection.py`
- Create: `terminal_prime/database/schema.py`
- Create: `tests/test_database.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_database.py
import sqlite3
import os
import tempfile
from terminal_prime.database.connection import get_connection, close_connection
from terminal_prime.database.schema import create_tables


def test_create_tables():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        conn = get_connection(db_path)
        create_tables(conn)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        assert "clients" in tables
        assert "affiliates" in tables
        assert "invoices" in tables
        assert "payments" in tables
        close_connection()
    finally:
        os.unlink(db_path)


def test_foreign_keys_enabled():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        conn = get_connection(db_path)
        cursor = conn.execute("PRAGMA foreign_keys")
        assert cursor.fetchone()[0] == 1
        close_connection()
    finally:
        os.unlink(db_path)


def test_unique_constraints():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        conn = get_connection(db_path)
        create_tables(conn)
        conn.execute("INSERT INTO clients (name) VALUES ('TEST')")
        conn.commit()
        try:
            conn.execute("INSERT INTO clients (name) VALUES ('TEST')")
            conn.commit()
            assert False, "Should have raised IntegrityError"
        except sqlite3.IntegrityError:
            pass
        close_connection()
    finally:
        os.unlink(db_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_database.py -v`
Expected: FAIL

- [ ] **Step 3: Implement connection and schema**

```python
# terminal_prime/database/connection.py
import sqlite3
from typing import Optional

_connection: Optional[sqlite3.Connection] = None


def get_connection(db_path: str = "terminal_prime.db") -> sqlite3.Connection:
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(db_path)
        _connection.execute("PRAGMA foreign_keys = ON")
        _connection.row_factory = sqlite3.Row
    return _connection


def close_connection():
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
```

```python
# terminal_prime/database/schema.py
import sqlite3


def create_tables(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            contact_email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS affiliates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            client_id INTEGER NOT NULL REFERENCES clients(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, client_id)
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL UNIQUE,
            client_id INTEGER NOT NULL REFERENCES clients(id),
            affiliate_id INTEGER NOT NULL REFERENCES affiliates(id),
            date DATE NOT NULL,
            due_date DATE NOT NULL,
            amount INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'EN_ATTENTE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL REFERENCES invoices(id),
            client_id INTEGER NOT NULL REFERENCES clients(id),
            date DATE NOT NULL,
            amount INTEGER NOT NULL,
            mode TEXT NOT NULL,
            reference TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_database.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add terminal_prime/database/connection.py terminal_prime/database/schema.py tests/test_database.py
git commit -m "feat: add SQLite connection singleton and schema creation"
```

---

### Task 4: Repositories (CRUD)

**Files:**
- Create: `terminal_prime/database/client_repo.py`
- Create: `terminal_prime/database/affiliate_repo.py`
- Create: `terminal_prime/database/invoice_repo.py`
- Create: `terminal_prime/database/payment_repo.py`
- Create: `tests/test_repos.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_repos.py
import os
import tempfile
from datetime import date
from terminal_prime.database.connection import get_connection, close_connection
from terminal_prime.database.schema import create_tables
from terminal_prime.database.client_repo import ClientRepo
from terminal_prime.database.affiliate_repo import AffiliateRepo
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.database.payment_repo import PaymentRepo
from terminal_prime.models.invoice import InvoiceStatus
from terminal_prime.models.payment import PaymentMode
import pytest


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    conn = get_connection(db_path)
    create_tables(conn)
    yield conn
    close_connection()
    os.unlink(db_path)


def test_client_crud(db):
    repo = ClientRepo(db)
    client_id = repo.create("MCI CARE CI", "contact@mci.ci")
    assert client_id > 0
    client = repo.get_by_id(client_id)
    assert client.name == "MCI CARE CI"
    all_clients = repo.get_all()
    assert len(all_clients) == 1


def test_client_get_or_create(db):
    repo = ClientRepo(db)
    id1 = repo.get_or_create("MCI CARE CI")
    id2 = repo.get_or_create("MCI CARE CI")
    assert id1 == id2
    assert len(repo.get_all()) == 1


def test_affiliate_crud(db):
    repo_c = ClientRepo(db)
    client_id = repo_c.create("MCI CARE CI")
    repo_a = AffiliateRepo(db)
    aff_id = repo_a.create("SERVAIRE ABIDJAN", client_id)
    assert aff_id > 0
    aff = repo_a.get_by_id(aff_id)
    assert aff.name == "SERVAIRE ABIDJAN"


def test_affiliate_get_or_create(db):
    repo_c = ClientRepo(db)
    client_id = repo_c.create("MCI CARE CI")
    repo_a = AffiliateRepo(db)
    id1 = repo_a.get_or_create("SERVAIRE ABIDJAN", client_id)
    id2 = repo_a.get_or_create("SERVAIRE ABIDJAN", client_id)
    assert id1 == id2


def test_invoice_crud(db):
    repo_c = ClientRepo(db)
    cid = repo_c.create("MCI CARE CI")
    repo_a = AffiliateRepo(db)
    aid = repo_a.create("SERVAIRE ABIDJAN", cid)
    repo_i = InvoiceRepo(db)
    inv_id = repo_i.create(
        number="0112-3112-2431928", client_id=cid, affiliate_id=aid,
        inv_date=date(2025, 1, 1), due_date=date(2025, 1, 31),
        amount=7576
    )
    assert inv_id > 0
    inv = repo_i.get_by_id(inv_id)
    assert inv.amount == 7576
    assert inv.status == InvoiceStatus.EN_ATTENTE


def test_invoice_duplicate_ignored(db):
    repo_c = ClientRepo(db)
    cid = repo_c.create("MCI CARE CI")
    repo_a = AffiliateRepo(db)
    aid = repo_a.create("SERVAIRE ABIDJAN", cid)
    repo_i = InvoiceRepo(db)
    repo_i.create("DUP-001", cid, aid, date(2025, 1, 1), date(2025, 1, 31), 1000)
    result = repo_i.create_if_not_exists("DUP-001", cid, aid, date(2025, 1, 1), date(2025, 1, 31), 1000)
    assert result is None


def test_invoice_with_payments(db):
    repo_c = ClientRepo(db)
    cid = repo_c.create("MCI CARE CI")
    repo_a = AffiliateRepo(db)
    aid = repo_a.create("SERVAIRE ABIDJAN", cid)
    repo_i = InvoiceRepo(db)
    inv_id = repo_i.create("PAY-TEST-001", cid, aid, date(2025, 1, 1), date(2025, 1, 31), 10000)
    repo_p = PaymentRepo(db)
    repo_p.create(inv_id, cid, date(2025, 2, 1), 6000, PaymentMode.VIREMENT)
    inv = repo_i.get_by_id(inv_id)
    assert inv.total_paid == 6000
    assert inv.remaining == 4000


def test_payment_crud(db):
    repo_c = ClientRepo(db)
    cid = repo_c.create("MCI CARE CI")
    repo_a = AffiliateRepo(db)
    aid = repo_a.create("SERVAIRE ABIDJAN", cid)
    repo_i = InvoiceRepo(db)
    inv_id = repo_i.create("INV-PAY-001", cid, aid, date(2025, 1, 1), date(2025, 1, 31), 10000)
    repo_p = PaymentRepo(db)
    pay_id = repo_p.create(inv_id, cid, date(2025, 2, 1), 5000, PaymentMode.CHEQUE)
    assert pay_id > 0
    payments = repo_p.get_by_invoice(inv_id)
    assert len(payments) == 1
    assert payments[0].amount == 5000


def test_payment_updates_invoice_status(db):
    repo_c = ClientRepo(db)
    cid = repo_c.create("MCI CARE CI")
    repo_a = AffiliateRepo(db)
    aid = repo_a.create("SERVAIRE ABIDJAN", cid)
    repo_i = InvoiceRepo(db)
    inv_id = repo_i.create("STAT-001", cid, aid, date(2025, 1, 1), date(2025, 1, 31), 10000)
    repo_p = PaymentRepo(db)
    # Partial payment
    repo_p.create(inv_id, cid, date(2025, 2, 1), 6000, PaymentMode.VIREMENT)
    repo_i.update_status_from_payments(inv_id)
    inv = repo_i.get_by_id(inv_id)
    assert inv.status == InvoiceStatus.PARTIELLE
    # Full payment
    repo_p.create(inv_id, cid, date(2025, 2, 10), 4000, PaymentMode.ESPECES)
    repo_i.update_status_from_payments(inv_id)
    inv = repo_i.get_by_id(inv_id)
    assert inv.status == InvoiceStatus.PAYEE
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_repos.py -v`
Expected: FAIL

- [ ] **Step 3: Implement repositories**

```python
# terminal_prime/database/client_repo.py
import sqlite3
from typing import List, Optional
from terminal_prime.models.client import Client


class ClientRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, name: str, contact_email: str = None) -> int:
        cursor = self.conn.execute(
            "INSERT INTO clients (name, contact_email) VALUES (?, ?)",
            (name, contact_email)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_or_create(self, name: str) -> int:
        row = self.conn.execute(
            "SELECT id FROM clients WHERE name = ?", (name,)
        ).fetchone()
        if row:
            return row["id"]
        return self.create(name)

    def get_by_id(self, client_id: int) -> Optional[Client]:
        row = self.conn.execute(
            "SELECT * FROM clients WHERE id = ?", (client_id,)
        ).fetchone()
        if not row:
            return None
        return Client(id=row["id"], name=row["name"], contact_email=row["contact_email"])

    def get_all(self) -> List[Client]:
        rows = self.conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
        return [Client(id=r["id"], name=r["name"], contact_email=r["contact_email"]) for r in rows]

    def search(self, query: str) -> List[Client]:
        rows = self.conn.execute(
            "SELECT * FROM clients WHERE name LIKE ? ORDER BY name",
            (f"%{query}%",)
        ).fetchall()
        return [Client(id=r["id"], name=r["name"], contact_email=r["contact_email"]) for r in rows]
```

```python
# terminal_prime/database/affiliate_repo.py
import sqlite3
from typing import List, Optional
from terminal_prime.models.affiliate import Affiliate


class AffiliateRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, name: str, client_id: int) -> int:
        cursor = self.conn.execute(
            "INSERT INTO affiliates (name, client_id) VALUES (?, ?)",
            (name, client_id)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_or_create(self, name: str, client_id: int) -> int:
        row = self.conn.execute(
            "SELECT id FROM affiliates WHERE name = ? AND client_id = ?",
            (name, client_id)
        ).fetchone()
        if row:
            return row["id"]
        return self.create(name, client_id)

    def get_by_id(self, aff_id: int) -> Optional[Affiliate]:
        row = self.conn.execute(
            "SELECT * FROM affiliates WHERE id = ?", (aff_id,)
        ).fetchone()
        if not row:
            return None
        return Affiliate(id=row["id"], name=row["name"], client_id=row["client_id"])

    def get_by_client(self, client_id: int) -> List[Affiliate]:
        rows = self.conn.execute(
            "SELECT * FROM affiliates WHERE client_id = ? ORDER BY name",
            (client_id,)
        ).fetchall()
        return [Affiliate(id=r["id"], name=r["name"], client_id=r["client_id"]) for r in rows]
```

```python
# terminal_prime/database/invoice_repo.py
import sqlite3
from datetime import date
from typing import List, Optional, Tuple
from terminal_prime.models.invoice import Invoice, InvoiceStatus


class InvoiceRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, number: str, client_id: int, affiliate_id: int,
               inv_date: date, due_date: date, amount: int) -> int:
        cursor = self.conn.execute(
            """INSERT INTO invoices (number, client_id, affiliate_id, date, due_date, amount, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (number, client_id, affiliate_id, str(inv_date), str(due_date), amount, InvoiceStatus.EN_ATTENTE.value)
        )
        self.conn.commit()
        return cursor.lastrowid

    def create_if_not_exists(self, number: str, client_id: int, affiliate_id: int,
                              inv_date: date, due_date: date, amount: int) -> Optional[int]:
        existing = self.conn.execute(
            "SELECT id FROM invoices WHERE number = ?", (number,)
        ).fetchone()
        if existing:
            return None
        return self.create(number, client_id, affiliate_id, inv_date, due_date, amount)

    def get_by_id(self, inv_id: int) -> Optional[Invoice]:
        row = self.conn.execute(
            """SELECT i.*, c.name as client_name, a.name as affiliate_name,
                      COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0) as total_paid
               FROM invoices i
               JOIN clients c ON i.client_id = c.id
               JOIN affiliates a ON i.affiliate_id = a.id
               WHERE i.id = ?""",
            (inv_id,)
        ).fetchone()
        if not row:
            return None
        return self._row_to_invoice(row)

    def get_all(self, status: str = None, client_id: int = None,
                limit: int = 10, offset: int = 0) -> Tuple[List[Invoice], int]:
        query = """SELECT i.*, c.name as client_name, a.name as affiliate_name,
                          COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0) as total_paid
                   FROM invoices i
                   JOIN clients c ON i.client_id = c.id
                   JOIN affiliates a ON i.affiliate_id = a.id"""
        params = []
        conditions = []
        if status:
            conditions.append("i.status = ?")
            params.append(status)
        if client_id:
            conditions.append("i.client_id = ?")
            params.append(client_id)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        count_query = f"SELECT COUNT(*) FROM ({query})"
        total = self.conn.execute(count_query, params).fetchone()[0]

        query += " ORDER BY i.date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.conn.execute(query, params).fetchall()
        return [self._row_to_invoice(r) for r in rows], total

    def get_unpaid(self) -> List[Invoice]:
        rows = self.conn.execute(
            """SELECT i.*, c.name as client_name, a.name as affiliate_name,
                      COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0) as total_paid
               FROM invoices i
               JOIN clients c ON i.client_id = c.id
               JOIN affiliates a ON i.affiliate_id = a.id
               WHERE i.status != ?
               ORDER BY i.due_date ASC""",
            (InvoiceStatus.PAYEE.value,)
        ).fetchall()
        return [self._row_to_invoice(r) for r in rows]

    def update_status_from_payments(self, inv_id: int):
        row = self.conn.execute(
            """SELECT i.amount,
                      COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0) as paid
               FROM invoices i WHERE i.id = ?""",
            (inv_id,)
        ).fetchone()
        if not row:
            return
        if row["paid"] >= row["amount"]:
            new_status = InvoiceStatus.PAYEE.value
        elif row["paid"] > 0:
            new_status = InvoiceStatus.PARTIELLE.value
        else:
            new_status = InvoiceStatus.EN_ATTENTE.value
        self.conn.execute(
            "UPDATE invoices SET status = ? WHERE id = ?",
            (new_status, inv_id)
        )
        self.conn.commit()

    def _row_to_invoice(self, row) -> Invoice:
        return Invoice(
            id=row["id"], number=row["number"],
            client_id=row["client_id"], affiliate_id=row["affiliate_id"],
            date=date.fromisoformat(row["date"]),
            due_date=date.fromisoformat(row["due_date"]),
            amount=row["amount"],
            status=InvoiceStatus(row["status"]),
            total_paid=row["total_paid"],
            client_name=row["client_name"],
            affiliate_name=row["affiliate_name"],
        )
```

```python
# terminal_prime/database/payment_repo.py
import sqlite3
from datetime import date
from typing import List
from terminal_prime.models.payment import Payment, PaymentMode


class PaymentRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, invoice_id: int, client_id: int, pay_date: date,
               amount: int, mode: PaymentMode, reference: str = None) -> int:
        if reference is None:
            count = self.conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
            reference = f"PAY-{count + 1:05d}"
        cursor = self.conn.execute(
            """INSERT INTO payments (invoice_id, client_id, date, amount, mode, reference)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (invoice_id, client_id, str(pay_date), amount, mode.value, reference)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_by_invoice(self, invoice_id: int) -> List[Payment]:
        rows = self.conn.execute(
            "SELECT * FROM payments WHERE invoice_id = ? ORDER BY date DESC",
            (invoice_id,)
        ).fetchall()
        return [self._row_to_payment(r) for r in rows]

    def get_recent(self, limit: int = 5) -> List[Payment]:
        rows = self.conn.execute(
            "SELECT * FROM payments ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [self._row_to_payment(r) for r in rows]

    def get_total_collected_mtd(self) -> int:
        today = date.today()
        first_of_month = today.replace(day=1)
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE date >= ?",
            (str(first_of_month),)
        ).fetchone()
        return row[0]

    def _row_to_payment(self, row) -> Payment:
        return Payment(
            id=row["id"], invoice_id=row["invoice_id"],
            client_id=row["client_id"],
            date=date.fromisoformat(row["date"]),
            amount=row["amount"],
            mode=PaymentMode(row["mode"]),
            reference=row["reference"],
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_repos.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add terminal_prime/database/ tests/test_repos.py
git commit -m "feat: add CRUD repositories for all entities"
```

---

### Task 5: Theme module

**Files:**
- Create: `terminal_prime/theme.py`

- [ ] **Step 1: Create theme.py**

```python
# terminal_prime/theme.py
"""Carbon Console Design System - all visual constants."""

# Surfaces (deep -> elevated)
SURFACE_LOWEST = "#0e0e0e"
SURFACE = "#131313"
SURFACE_LOW = "#1c1b1b"
SURFACE_CONT = "#20201f"
SURFACE_HIGH = "#2a2a2a"
SURFACE_BRIGHT = "#393939"
SURFACE_HIGHEST = "#353535"

# Semantic colors
PRIMARY = "#a5c8ff"
PRIMARY_CONT = "#1f538d"
SECONDARY = "#b7c7e4"
SECONDARY_CONT = "#3a4a61"
TERTIARY = "#fdbb2e"
TERTIARY_CONT = "#6d4c00"
ERROR = "#ffb4ab"
ERROR_CONT = "#93000a"

# Text
ON_SURFACE = "#e5e2e1"
ON_SURFACE_VAR = "#c2c6d1"
ON_PRIMARY = "#00315e"
ON_ERROR = "#690005"
OUTLINE = "#8c919b"
OUTLINE_VAR = "#424750"

# Design rules
CORNER_RADIUS = 10
FONT_FAMILY = "Inter"
FONT_HEADING = (FONT_FAMILY, 24, "bold")
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_BODY = (FONT_FAMILY, 14)
FONT_BODY_BOLD = (FONT_FAMILY, 14, "bold")
FONT_LABEL = (FONT_FAMILY, 11)
FONT_LABEL_UPPER = (FONT_FAMILY, 10, "bold")
FONT_SMALL = (FONT_FAMILY, 10)
FONT_KPI = (FONT_FAMILY, 32, "bold")

# Status pill colors: (bg, fg)
STATUS_COLORS = {
    "EN_ATTENTE": (SURFACE_HIGHEST, ON_SURFACE_VAR),
    "PAYEE": (TERTIARY_CONT, TERTIARY),
    "PARTIELLE": (SECONDARY_CONT, SECONDARY),
    "EN_RETARD": (ERROR_CONT, ERROR),
}

# Window
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 700
SIDEBAR_WIDTH = 250


def format_fcfa(amount: int) -> str:
    """Format integer amount as FCFA string: 1 234 500 FCFA"""
    return f"{amount:,.0f} FCFA".replace(",", " ")
```

- [ ] **Step 2: Commit**

```bash
git add terminal_prime/theme.py
git commit -m "feat: add Carbon Console theme constants"
```

---

### Task 6: Import service (Mediciel Excel)

**Files:**
- Create: `terminal_prime/services/import_service.py`
- Create: `tests/test_import_service.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_import_service.py
import os
import tempfile
from datetime import date
from openpyxl import Workbook
from terminal_prime.database.connection import get_connection, close_connection
from terminal_prime.database.schema import create_tables
from terminal_prime.services.import_service import ImportService
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.database.client_repo import ClientRepo
import pytest


def _create_test_xlsx(path: str, rows: list):
    """Create a test xlsx with Mediciel-format columns."""
    wb = Workbook()
    ws = wb.active
    headers = ["M", "S", "Date facture", "Client principal", "Affilié",
               "N° Facture", "Montant Total", "Règlement", "Solde", "!",
               "Statut Envoi", "Date Envoi", "Code Recap. Client"]
    ws.append(headers)
    for row in rows:
        ws.append(row)
    wb.save(path)


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    conn = get_connection(db_path)
    create_tables(conn)
    yield conn
    close_connection()
    os.unlink(db_path)


def test_import_basic(db):
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        xlsx_path = f.name
    try:
        _create_test_xlsx(xlsx_path, [
            [0, 0, date(2025, 1, 1), "MCI CARE CI", "SERVAIRE ABIDJAN",
             "0112-3112-2431928", 7576, 7576, 0, "", "NON ENVOYEE", "", ""],
            [0, 0, date(2025, 1, 1), "MCI CARE CI", "TEYLIOM GROUP",
             "0112-3112-2431934", 140316, 140316, 0, "", "NON ENVOYEE", "", ""],
        ])
        service = ImportService(db)
        result = service.import_file(xlsx_path)
        assert result["imported"] == 2
        assert result["duplicates"] == 0
        assert result["clients_created"] >= 1
    finally:
        os.unlink(xlsx_path)


def test_import_duplicates(db):
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        xlsx_path = f.name
    try:
        _create_test_xlsx(xlsx_path, [
            [0, 0, date(2025, 1, 1), "MCI CARE CI", "SERVAIRE ABIDJAN",
             "DUP-001", 5000, 0, 5000, "", "NON ENVOYEE", "", ""],
        ])
        service = ImportService(db)
        result1 = service.import_file(xlsx_path)
        assert result1["imported"] == 1
        result2 = service.import_file(xlsx_path)
        assert result2["imported"] == 0
        assert result2["duplicates"] == 1
    finally:
        os.unlink(xlsx_path)


def test_import_due_date_30_days(db):
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        xlsx_path = f.name
    try:
        _create_test_xlsx(xlsx_path, [
            [0, 0, date(2025, 3, 15), "TEST ASSUR", "TEST AFF",
             "DATE-001", 10000, 0, 10000, "", "NON ENVOYEE", "", ""],
        ])
        service = ImportService(db)
        service.import_file(xlsx_path)
        repo = InvoiceRepo(db)
        invoices, _ = repo.get_all()
        assert invoices[0].due_date == date(2025, 4, 14)
    finally:
        os.unlink(xlsx_path)


def test_import_creates_clients_and_affiliates(db):
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        xlsx_path = f.name
    try:
        _create_test_xlsx(xlsx_path, [
            [0, 0, date(2025, 1, 1), "ASSUR A", "AFF 1", "F-001", 1000, 0, 1000, "", "", "", ""],
            [0, 0, date(2025, 1, 1), "ASSUR A", "AFF 2", "F-002", 2000, 0, 2000, "", "", "", ""],
            [0, 0, date(2025, 1, 1), "ASSUR B", "AFF 3", "F-003", 3000, 0, 3000, "", "", "", ""],
        ])
        service = ImportService(db)
        result = service.import_file(xlsx_path)
        assert result["clients_created"] == 2
        assert result["affiliates_created"] == 3
    finally:
        os.unlink(xlsx_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_import_service.py -v`
Expected: FAIL

- [ ] **Step 3: Implement import service**

```python
# terminal_prime/services/import_service.py
from datetime import date, timedelta
from openpyxl import load_workbook
from terminal_prime.database.client_repo import ClientRepo
from terminal_prime.database.affiliate_repo import AffiliateRepo
from terminal_prime.database.invoice_repo import InvoiceRepo


class ImportService:
    def __init__(self, conn):
        self.conn = conn
        self.client_repo = ClientRepo(conn)
        self.affiliate_repo = AffiliateRepo(conn)
        self.invoice_repo = InvoiceRepo(conn)

    def import_file(self, filepath: str) -> dict:
        wb = load_workbook(filepath, read_only=True, data_only=True)
        ws = wb.active

        stats = {
            "imported": 0,
            "duplicates": 0,
            "clients_created": 0,
            "affiliates_created": 0,
            "errors": 0,
        }

        rows = list(ws.iter_rows(min_row=2, values_only=True))
        wb.close()

        existing_clients = {c.name: c.id for c in self.client_repo.get_all()}
        existing_affiliates = {}

        for row in rows:
            if len(row) < 7 or not row[5]:
                stats["errors"] += 1
                continue

            inv_date = self._parse_date(row[2])
            client_name = str(row[3]).strip() if row[3] else None
            affiliate_name = str(row[4]).strip() if row[4] else None
            number = str(row[5]).strip()
            amount = int(row[6]) if row[6] else 0

            if not client_name or not number or not inv_date:
                stats["errors"] += 1
                continue

            # Get or create client
            if client_name in existing_clients:
                client_id = existing_clients[client_name]
            else:
                client_id = self.client_repo.create(client_name)
                existing_clients[client_name] = client_id
                stats["clients_created"] += 1

            # Get or create affiliate
            aff_key = (affiliate_name, client_id)
            if affiliate_name and aff_key in existing_affiliates:
                affiliate_id = existing_affiliates[aff_key]
            elif affiliate_name:
                affiliate_id = self.affiliate_repo.get_or_create(affiliate_name, client_id)
                if aff_key not in existing_affiliates:
                    stats["affiliates_created"] += 1
                existing_affiliates[aff_key] = affiliate_id
            else:
                stats["errors"] += 1
                continue

            due_date = inv_date + timedelta(days=30)
            result = self.invoice_repo.create_if_not_exists(
                number, client_id, affiliate_id, inv_date, due_date, amount
            )
            if result is None:
                stats["duplicates"] += 1
            else:
                stats["imported"] += 1

        return stats

    def _parse_date(self, value) -> date:
        if isinstance(value, date):
            return value
        if isinstance(value, (int, float)):
            # Excel serial date: days since 1899-12-30
            from datetime import datetime, timedelta
            return (datetime(1899, 12, 30) + timedelta(days=int(value))).date()
        if isinstance(value, str):
            return date.fromisoformat(value)
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_import_service.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add terminal_prime/services/import_service.py tests/test_import_service.py
git commit -m "feat: add Mediciel Excel import service"
```

---

### Task 7: Aging and dashboard services

**Files:**
- Create: `terminal_prime/services/aging_service.py`
- Create: `terminal_prime/services/dashboard_service.py`
- Create: `tests/test_services.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_services.py
import os
import tempfile
from datetime import date, timedelta
from terminal_prime.database.connection import get_connection, close_connection
from terminal_prime.database.schema import create_tables
from terminal_prime.database.client_repo import ClientRepo
from terminal_prime.database.affiliate_repo import AffiliateRepo
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.database.payment_repo import PaymentRepo
from terminal_prime.services.aging_service import AgingService
from terminal_prime.services.dashboard_service import DashboardService
from terminal_prime.models.payment import PaymentMode
import pytest


@pytest.fixture
def db_with_data():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    conn = get_connection(db_path)
    create_tables(conn)
    cr = ClientRepo(conn)
    ar = AffiliateRepo(conn)
    ir = InvoiceRepo(conn)
    pr = PaymentRepo(conn)
    cid = cr.create("ASSUREUR A")
    aid = ar.create("AFFILIE 1", cid)
    today = date.today()
    # Recent invoice (0-30 days)
    ir.create("INV-001", cid, aid, today - timedelta(days=10), today + timedelta(days=20), 100000)
    # 31-60 days overdue
    ir.create("INV-002", cid, aid, today - timedelta(days=50), today - timedelta(days=20), 200000)
    # 61-90 days overdue
    ir.create("INV-003", cid, aid, today - timedelta(days=80), today - timedelta(days=50), 150000)
    # +90 days overdue
    ir.create("INV-004", cid, aid, today - timedelta(days=120), today - timedelta(days=90), 300000)
    # Paid invoice
    inv_id = ir.create("INV-005", cid, aid, today - timedelta(days=5), today + timedelta(days=25), 50000)
    pr.create(inv_id, cid, today, 50000, PaymentMode.VIREMENT)
    ir.update_status_from_payments(inv_id)
    yield conn
    close_connection()
    os.unlink(db_path)


def test_aging_buckets(db_with_data):
    service = AgingService(db_with_data)
    buckets = service.get_aging_buckets()
    assert "0-30" in buckets
    assert "31-60" in buckets
    assert "61-90" in buckets
    assert "90+" in buckets
    assert buckets["0-30"] == 100000
    assert buckets["31-60"] == 200000
    assert buckets["61-90"] == 150000
    assert buckets["90+"] == 300000


def test_dashboard_kpis(db_with_data):
    service = DashboardService(db_with_data)
    kpis = service.get_kpis()
    assert kpis["total_issued"] == 800000
    assert kpis["total_collected"] == 50000
    assert kpis["outstanding"] == 750000


def test_top_debtors(db_with_data):
    service = DashboardService(db_with_data)
    debtors = service.get_top_debtors(limit=5)
    assert len(debtors) >= 1
    assert debtors[0]["total_due"] > 0


def test_dso_calculation(db_with_data):
    service = DashboardService(db_with_data)
    dso = service.get_dso()
    assert isinstance(dso, float)
    assert dso >= 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_services.py -v`
Expected: FAIL

- [ ] **Step 3: Implement services**

```python
# terminal_prime/services/aging_service.py
from datetime import date
from typing import Dict, List


class AgingService:
    def __init__(self, conn):
        self.conn = conn

    def get_aging_buckets(self, today: date = None) -> Dict[str, int]:
        today = today or date.today()
        rows = self.conn.execute(
            """SELECT i.due_date, i.amount,
                      COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0) as paid
               FROM invoices i
               WHERE i.status != 'PAYEE'"""
        ).fetchall()

        buckets = {"0-30": 0, "31-60": 0, "61-90": 0, "90+": 0}
        for row in rows:
            remaining = row["amount"] - row["paid"]
            if remaining <= 0:
                continue
            due = date.fromisoformat(row["due_date"])
            days_overdue = (today - due).days
            if days_overdue <= 0:
                buckets["0-30"] += remaining
            elif days_overdue <= 30:
                buckets["0-30"] += remaining
            elif days_overdue <= 60:
                buckets["31-60"] += remaining
            elif days_overdue <= 90:
                buckets["61-90"] += remaining
            else:
                buckets["90+"] += remaining
        return buckets

    def get_client_aging(self, client_id: int, today: date = None) -> Dict[str, int]:
        today = today or date.today()
        rows = self.conn.execute(
            """SELECT i.due_date, i.amount,
                      COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0) as paid
               FROM invoices i
               WHERE i.client_id = ? AND i.status != 'PAYEE'""",
            (client_id,)
        ).fetchall()

        buckets = {"current": 0, "0-30": 0, "31-60": 0, "61-90": 0, "90+": 0}
        for row in rows:
            remaining = row["amount"] - row["paid"]
            if remaining <= 0:
                continue
            due = date.fromisoformat(row["due_date"])
            days_overdue = (today - due).days
            if days_overdue <= 0:
                buckets["current"] += remaining
            elif days_overdue <= 30:
                buckets["0-30"] += remaining
            elif days_overdue <= 60:
                buckets["31-60"] += remaining
            elif days_overdue <= 90:
                buckets["61-90"] += remaining
            else:
                buckets["90+"] += remaining
        return buckets
```

```python
# terminal_prime/services/dashboard_service.py
from datetime import date, timedelta
from typing import Dict, List


class DashboardService:
    def __init__(self, conn):
        self.conn = conn

    def get_kpis(self) -> Dict[str, int]:
        total_issued = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM invoices"
        ).fetchone()[0]
        total_collected = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM payments"
        ).fetchone()[0]
        return {
            "total_issued": total_issued,
            "total_collected": total_collected,
            "outstanding": total_issued - total_collected,
        }

    def get_top_debtors(self, limit: int = 5) -> List[Dict]:
        rows = self.conn.execute(
            """SELECT c.id, c.name,
                      SUM(i.amount) as total_invoiced,
                      COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.client_id = c.id), 0) as total_paid
               FROM invoices i
               JOIN clients c ON i.client_id = c.id
               WHERE i.status != 'PAYEE'
               GROUP BY c.id
               ORDER BY (SUM(i.amount) - COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.client_id = c.id), 0)) DESC
               LIMIT ?""",
            (limit,)
        ).fetchall()
        result = []
        for r in rows:
            total_due = r["total_invoiced"] - r["total_paid"]
            if total_due > 0:
                result.append({
                    "id": r["id"],
                    "name": r["name"],
                    "total_due": total_due,
                })
        return result

    def get_dso(self) -> float:
        today = date.today()
        start = today - timedelta(days=90)
        outstanding = self.conn.execute(
            """SELECT COALESCE(SUM(i.amount) -
                      (SELECT COALESCE(SUM(p.amount), 0) FROM payments p), 0)
               FROM invoices i"""
        ).fetchone()[0]
        credit_sales = self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE date >= ?",
            (str(start),)
        ).fetchone()[0]
        if credit_sales == 0:
            return 0.0
        return (outstanding / credit_sales) * 90

    def get_collection_rate(self) -> float:
        kpis = self.get_kpis()
        if kpis["total_issued"] == 0:
            return 0.0
        return (kpis["total_collected"] / kpis["total_issued"]) * 100
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_services.py -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add terminal_prime/services/aging_service.py terminal_prime/services/dashboard_service.py tests/test_services.py
git commit -m "feat: add aging and dashboard services"
```

---

## Chunk 2: UI Components

### Task 8: App shell (sidebar + topbar + frame navigation)

**Files:**
- Create: `terminal_prime/app.py`
- Create: `terminal_prime/components/sidebar.py`
- Create: `terminal_prime/components/topbar.py`

- [ ] **Step 1: Create sidebar component**

```python
# terminal_prime/components/sidebar.py
import customtkinter as ctk
from terminal_prime import theme


class Sidebar(ctk.CTkFrame):
    NAV_ITEMS = [
        ("dashboard", "Tableau de Bord"),
        ("invoices", "Factures"),
        ("collections", "Recouvrements"),
        ("analysis", "Analyse Client"),
        ("reports", "Rapports"),
    ]

    def __init__(self, parent, on_navigate):
        super().__init__(parent, width=theme.SIDEBAR_WIDTH, corner_radius=0,
                         fg_color=theme.SURFACE)
        self.on_navigate = on_navigate
        self.active_key = "dashboard"
        self.buttons = {}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(24, 40), sticky="w")
        logo_icon = ctk.CTkFrame(logo_frame, width=32, height=32,
                                  corner_radius=8, fg_color=theme.PRIMARY_CONT)
        logo_icon.pack(side="left", padx=(0, 10))
        logo_icon.pack_propagate(False)
        ctk.CTkLabel(logo_icon, text="T", font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left")
        ctk.CTkLabel(title_frame, text="Terminal Prime",
                     font=(theme.FONT_FAMILY, 16, "bold"),
                     text_color=theme.PRIMARY).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="ACCOUNTING DEPT",
                     font=(theme.FONT_FAMILY, 9, "bold"),
                     text_color=theme.ON_SURFACE_VAR).pack(anchor="w")

        # Nav buttons
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.grid(row=1, column=0, sticky="new", padx=8)
        for key, label in self.NAV_ITEMS:
            btn = ctk.CTkButton(
                nav_frame, text=label, anchor="w",
                height=44, corner_radius=theme.CORNER_RADIUS,
                font=theme.FONT_BODY,
                fg_color="transparent",
                text_color=theme.ON_SURFACE_VAR,
                hover_color=theme.SURFACE_HIGH,
                command=lambda k=key: self._on_click(k),
            )
            btn.pack(fill="x", pady=2)
            self.buttons[key] = btn

        # Profile section
        profile_frame = ctk.CTkFrame(self, fg_color=theme.SURFACE_LOW,
                                      corner_radius=theme.CORNER_RADIUS)
        profile_frame.grid(row=2, column=0, padx=16, pady=20, sticky="sew")
        ctk.CTkLabel(profile_frame, text="Utilisateur",
                     font=theme.FONT_BODY_BOLD,
                     text_color=theme.ON_SURFACE).pack(padx=16, pady=(12, 2), anchor="w")
        ctk.CTkLabel(profile_frame, text="Comptable",
                     font=theme.FONT_SMALL,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=16, pady=(0, 12), anchor="w")

        self._update_active()

    def _on_click(self, key: str):
        self.active_key = key
        self._update_active()
        self.on_navigate(key)

    def _update_active(self):
        for key, btn in self.buttons.items():
            if key == self.active_key:
                btn.configure(fg_color=theme.PRIMARY_CONT, text_color="white",
                              hover_color=theme.PRIMARY_CONT)
            else:
                btn.configure(fg_color="transparent", text_color=theme.ON_SURFACE_VAR,
                              hover_color=theme.SURFACE_HIGH)
```

- [ ] **Step 2: Create topbar component**

```python
# terminal_prime/components/topbar.py
import customtkinter as ctk
from terminal_prime import theme


class Topbar(ctk.CTkFrame):
    def __init__(self, parent, title: str = "Commercial Balance"):
        super().__init__(parent, height=64, corner_radius=0,
                         fg_color=theme.SURFACE)
        self.pack_propagate(False)

        self.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(self, text=title,
                     font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color=theme.PRIMARY).grid(
            row=0, column=0, padx=32, pady=16, sticky="w")

        # Search
        self.search_var = ctk.StringVar()
        search = ctk.CTkEntry(
            self, textvariable=self.search_var,
            placeholder_text="Rechercher...",
            width=350, height=36,
            corner_radius=theme.CORNER_RADIUS,
            fg_color=theme.SURFACE_LOWEST,
            border_width=0,
            font=theme.FONT_BODY,
            text_color=theme.ON_SURFACE,
        )
        search.grid(row=0, column=1, padx=16, pady=16, sticky="w")
```

- [ ] **Step 3: Create app.py with frame navigation**

```python
# terminal_prime/app.py
import customtkinter as ctk
from terminal_prime import theme
from terminal_prime.database.connection import get_connection, close_connection
from terminal_prime.database.schema import create_tables
from terminal_prime.components.sidebar import Sidebar
from terminal_prime.components.topbar import Topbar


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Terminal Prime - Balance Commerciale")
        self.geometry(f"{theme.WINDOW_WIDTH}x{theme.WINDOW_HEIGHT}")
        self.minsize(theme.WINDOW_MIN_WIDTH, theme.WINDOW_MIN_HEIGHT)
        self.configure(fg_color=theme.SURFACE)

        # Database
        self.conn = get_connection()
        create_tables(self.conn)

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self, on_navigate=self._navigate)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        # Main area
        main = ctk.CTkFrame(self, fg_color=theme.SURFACE, corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Topbar
        self.topbar = Topbar(main)
        self.topbar.grid(row=0, column=0, sticky="new")

        # Content container (stacked frames)
        self.content = ctk.CTkFrame(main, fg_color=theme.SURFACE, corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Create view frames (lazy - placeholder for now)
        self.views = {}
        self._create_placeholder_views()
        self._navigate("dashboard")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_placeholder_views(self):
        for key, label in Sidebar.NAV_ITEMS:
            frame = ctk.CTkFrame(self.content, fg_color=theme.SURFACE, corner_radius=0)
            frame.grid(row=0, column=0, sticky="nsew")
            ctk.CTkLabel(frame, text=label, font=theme.FONT_HEADING,
                         text_color=theme.ON_SURFACE).place(relx=0.5, rely=0.5, anchor="center")
            self.views[key] = frame

    def _navigate(self, key: str):
        for view in self.views.values():
            view.grid_remove()
        self.views[key].grid()

    def _on_close(self):
        close_connection()
        self.destroy()
```

- [ ] **Step 4: Test manually**

Run: `python -m terminal_prime.main`
Expected: Window opens with sidebar navigation, clicking items switches placeholder views.

- [ ] **Step 5: Commit**

```bash
git add terminal_prime/app.py terminal_prime/components/sidebar.py terminal_prime/components/topbar.py terminal_prime/main.py
git commit -m "feat: add app shell with sidebar navigation and topbar"
```

---

### Task 9: Reusable UI components

**Files:**
- Create: `terminal_prime/components/kpi_card.py`
- Create: `terminal_prime/components/data_grid.py`
- Create: `terminal_prime/components/status_pill.py`
- Create: `terminal_prime/components/bar_chart.py`
- Create: `terminal_prime/components/progress_bar.py`

- [ ] **Step 1: Create KPI card**

```python
# terminal_prime/components/kpi_card.py
import customtkinter as ctk
from terminal_prime import theme


class KpiCard(ctk.CTkFrame):
    def __init__(self, parent, label: str, value: str, badge: str = "",
                 badge_color: str = None, value_color: str = None):
        super().__init__(parent, fg_color=theme.SURFACE_CONT,
                         corner_radius=theme.CORNER_RADIUS)

        # Label
        ctk.CTkLabel(self, text=label.upper(),
                     font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(
            padx=24, pady=(20, 8), anchor="w")

        # Value
        ctk.CTkLabel(self, text=value,
                     font=theme.FONT_KPI,
                     text_color=value_color or theme.ON_SURFACE).pack(
            padx=24, anchor="w")

        # Badge
        if badge:
            badge_frame = ctk.CTkFrame(self, fg_color="transparent")
            badge_frame.pack(padx=24, pady=(8, 20), anchor="w")
            ctk.CTkLabel(badge_frame, text=badge,
                         font=theme.FONT_SMALL,
                         text_color=badge_color or theme.PRIMARY,
                         fg_color=theme.SURFACE_LOW,
                         corner_radius=12,
                         padx=8, pady=2).pack()

    def update_values(self, value: str, badge: str = ""):
        for widget in self.winfo_children():
            widget.destroy()
        self.__init__(self.master, "", value, badge)
```

- [ ] **Step 2: Create status pill**

```python
# terminal_prime/components/status_pill.py
import customtkinter as ctk
from terminal_prime import theme


class StatusPill(ctk.CTkLabel):
    def __init__(self, parent, status: str):
        colors = theme.STATUS_COLORS.get(status, (theme.SURFACE_HIGHEST, theme.ON_SURFACE_VAR))
        bg, fg = colors
        super().__init__(
            parent, text=status.replace("_", " "),
            font=theme.FONT_LABEL_UPPER,
            text_color=fg, fg_color=bg,
            corner_radius=4, padx=8, pady=2,
        )
```

- [ ] **Step 3: Create data grid**

```python
# terminal_prime/components/data_grid.py
import customtkinter as ctk
from typing import List, Tuple, Callable, Optional
from terminal_prime import theme


class DataGrid(ctk.CTkFrame):
    def __init__(self, parent, columns: List[Tuple[str, int]],
                 on_page_change: Optional[Callable] = None):
        super().__init__(parent, fg_color=theme.SURFACE_CONT,
                         corner_radius=theme.CORNER_RADIUS)
        self.columns = columns  # [(header, width), ...]
        self.on_page_change = on_page_change
        self.current_page = 0
        self.total_pages = 1

        # Header
        self.header = ctk.CTkFrame(self, fg_color=theme.SURFACE_LOW, corner_radius=0)
        self.header.pack(fill="x")
        for col_name, col_width in columns:
            ctk.CTkLabel(self.header, text=col_name.upper(), width=col_width,
                         font=theme.FONT_LABEL_UPPER,
                         text_color=theme.ON_SURFACE_VAR,
                         anchor="w").pack(side="left", padx=20, pady=12)

        # Body
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True)

        # Pagination
        self.pagination = ctk.CTkFrame(self, fg_color=theme.SURFACE_LOW, corner_radius=0)
        self.pagination.pack(fill="x")
        self.page_label = ctk.CTkLabel(self.pagination, text="",
                                        font=theme.FONT_LABEL_UPPER,
                                        text_color=theme.ON_SURFACE_VAR)
        self.page_label.pack(side="left", padx=20, pady=12)

        nav = ctk.CTkFrame(self.pagination, fg_color="transparent")
        nav.pack(side="right", padx=20, pady=8)
        self.btn_prev = ctk.CTkButton(nav, text="<", width=32, height=28,
                                       fg_color=theme.SURFACE_HIGH,
                                       corner_radius=theme.CORNER_RADIUS,
                                       command=self._prev_page)
        self.btn_prev.pack(side="left", padx=2)
        self.btn_next = ctk.CTkButton(nav, text=">", width=32, height=28,
                                       fg_color=theme.SURFACE_HIGH,
                                       corner_radius=theme.CORNER_RADIUS,
                                       command=self._next_page)
        self.btn_next.pack(side="left", padx=2)

    def set_data(self, rows: List[List], total: int, page: int, page_size: int):
        for widget in self.body.winfo_children():
            widget.destroy()

        self.current_page = page
        self.total_pages = max(1, (total + page_size - 1) // page_size)

        for i, row_data in enumerate(rows):
            bg = theme.SURFACE_LOW if i % 2 == 0 else theme.SURFACE_CONT
            row_frame = ctk.CTkFrame(self.body, fg_color=bg, corner_radius=0, height=52)
            row_frame.pack(fill="x")
            row_frame.pack_propagate(False)
            for j, (_, col_width) in enumerate(self.columns):
                cell = row_data[j] if j < len(row_data) else ""
                if isinstance(cell, ctk.CTkBaseClass):
                    cell.master = row_frame
                    cell.pack(side="left", padx=20, pady=8)
                else:
                    ctk.CTkLabel(row_frame, text=str(cell), width=col_width,
                                 font=theme.FONT_BODY,
                                 text_color=theme.ON_SURFACE,
                                 anchor="w").pack(side="left", padx=20, pady=8)

        start = page * page_size + 1
        end = min(start + page_size - 1, total)
        self.page_label.configure(text=f"AFFICHAGE {start}-{end} SUR {total}")

    def _prev_page(self):
        if self.current_page > 0 and self.on_page_change:
            self.on_page_change(self.current_page - 1)

    def _next_page(self):
        if self.current_page < self.total_pages - 1 and self.on_page_change:
            self.on_page_change(self.current_page + 1)
```

- [ ] **Step 4: Create bar chart (Canvas)**

```python
# terminal_prime/components/bar_chart.py
import customtkinter as ctk
from tkinter import Canvas
from typing import List, Tuple
from terminal_prime import theme


class BarChart(ctk.CTkFrame):
    def __init__(self, parent, title: str = "", subtitle: str = ""):
        super().__init__(parent, fg_color=theme.SURFACE_CONT,
                         corner_radius=theme.CORNER_RADIUS)
        if title:
            ctk.CTkLabel(self, text=title, font=theme.FONT_TITLE,
                         text_color=theme.ON_SURFACE).pack(
                padx=24, pady=(20, 2), anchor="w")
        if subtitle:
            ctk.CTkLabel(self, text=subtitle, font=theme.FONT_SMALL,
                         text_color=theme.ON_SURFACE_VAR).pack(
                padx=24, pady=(0, 16), anchor="w")

        self.canvas = Canvas(self, bg=theme.SURFACE_CONT, highlightthickness=0,
                             height=200)
        self.canvas.pack(fill="x", padx=24, pady=(0, 20))

    def set_data(self, bars: List[Tuple[str, int, str]]):
        """bars: [(label, value, color), ...]"""
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 400
        h = self.canvas.winfo_height() or 200
        if not bars:
            return

        max_val = max(v for _, v, _ in bars) or 1
        bar_width = (w - 40) // len(bars) - 20
        x = 30

        for label, value, color in bars:
            bar_height = int((value / max_val) * (h - 60))
            y_top = h - 30 - bar_height
            self.canvas.create_rectangle(
                x, y_top, x + bar_width, h - 30,
                fill=color, outline="", width=0
            )
            # Value label
            formatted = f"{value:,.0f}".replace(",", " ")
            self.canvas.create_text(
                x + bar_width // 2, y_top - 12,
                text=formatted, fill=color,
                font=(theme.FONT_FAMILY, 9, "bold")
            )
            # Category label
            self.canvas.create_text(
                x + bar_width // 2, h - 12,
                text=label, fill=theme.ON_SURFACE_VAR,
                font=(theme.FONT_FAMILY, 9, "bold")
            )
            x += bar_width + 20

    def redraw(self):
        self.canvas.update_idletasks()
```

- [ ] **Step 5: Create progress bar**

```python
# terminal_prime/components/progress_bar.py
import customtkinter as ctk
from tkinter import Canvas
from terminal_prime import theme


class GradientProgressBar(ctk.CTkFrame):
    def __init__(self, parent, label: str = "", value: float = 0,
                 max_label: str = ""):
        super().__init__(parent, fg_color="transparent")

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=label, font=theme.FONT_BODY_BOLD,
                     text_color=theme.ON_SURFACE).pack(side="left")
        ctk.CTkLabel(top, text=max_label, font=theme.FONT_BODY_BOLD,
                     text_color=theme.ON_SURFACE).pack(side="right")

        self.canvas = Canvas(self, bg=theme.SURFACE_LOWEST, highlightthickness=0,
                             height=8)
        self.canvas.pack(fill="x", pady=(4, 0))
        self._value = value
        self.canvas.bind("<Configure>", lambda e: self._draw())

    def _draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        fill_w = int(w * min(self._value / 100, 1.0))
        if fill_w > 0:
            self.canvas.create_rectangle(0, 0, fill_w, 8,
                                          fill=theme.PRIMARY, outline="")

    def set_value(self, value: float):
        self._value = value
        self._draw()
```

- [ ] **Step 6: Commit**

```bash
git add terminal_prime/components/
git commit -m "feat: add reusable UI components (KPI card, data grid, bar chart, status pill, progress bar)"
```

---

## Chunk 3: Views (5 screens)

### Task 10: Dashboard view

**Files:**
- Create: `terminal_prime/views/dashboard_view.py`
- Modify: `terminal_prime/app.py` (replace placeholder)

- [ ] **Step 1: Implement dashboard view**

```python
# terminal_prime/views/dashboard_view.py
import customtkinter as ctk
from terminal_prime import theme
from terminal_prime.components.kpi_card import KpiCard
from terminal_prime.components.bar_chart import BarChart
from terminal_prime.components.progress_bar import GradientProgressBar
from terminal_prime.components.data_grid import DataGrid
from terminal_prime.components.status_pill import StatusPill
from terminal_prime.services.dashboard_service import DashboardService
from terminal_prime.services.aging_service import AgingService


class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, parent, conn):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.dashboard_svc = DashboardService(conn)
        self.aging_svc = AgingService(conn)
        self._build_ui()

    def _build_ui(self):
        # KPI row
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", padx=32, pady=(32, 16))
        kpi_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="kpi")

        kpis = self.dashboard_svc.get_kpis()
        self.kpi_issued = KpiCard(kpi_row, "Total Emis",
                                   theme.format_fcfa(kpis["total_issued"]))
        self.kpi_issued.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        self.kpi_collected = KpiCard(kpi_row, "Total Recouvre",
                                      theme.format_fcfa(kpis["total_collected"]),
                                      badge_color=theme.TERTIARY)
        self.kpi_collected.grid(row=0, column=1, padx=8, sticky="nsew")

        self.kpi_outstanding = KpiCard(kpi_row, "Solde Global",
                                        theme.format_fcfa(kpis["outstanding"]),
                                        value_color=theme.ERROR)
        self.kpi_outstanding.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        # Middle row: aging chart + performance
        mid_row = ctk.CTkFrame(self, fg_color="transparent")
        mid_row.pack(fill="x", padx=32, pady=8)
        mid_row.grid_columnconfigure(0, weight=3)
        mid_row.grid_columnconfigure(1, weight=2)

        # Aging chart
        buckets = self.aging_svc.get_aging_buckets()
        self.aging_chart = BarChart(mid_row, "Balance Agee",
                                    "Repartition des creances par echeance")
        self.aging_chart.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        self.after(200, lambda: self.aging_chart.set_data([
            ("0-30j", buckets["0-30"], theme.PRIMARY),
            ("31-60j", buckets["31-60"], theme.TERTIARY),
            ("61-90j", buckets["61-90"], theme.TERTIARY_CONT),
            ("90+j", buckets["90+"], theme.ERROR),
        ]))

        # Performance
        perf_frame = ctk.CTkFrame(mid_row, fg_color=theme.SURFACE_CONT,
                                   corner_radius=theme.CORNER_RADIUS)
        perf_frame.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(perf_frame, text="Performance", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(20, 16), anchor="w")

        rate = self.dashboard_svc.get_collection_rate()
        self.progress = GradientProgressBar(perf_frame, "Taux de recouvrement",
                                             rate, f"{rate:.0f}%")
        self.progress.pack(fill="x", padx=24, pady=(0, 20))

        # DSO + CEI
        metrics_row = ctk.CTkFrame(perf_frame, fg_color="transparent")
        metrics_row.pack(fill="x", padx=24, pady=(0, 20))
        metrics_row.grid_columnconfigure((0, 1), weight=1, uniform="metric")

        dso_frame = ctk.CTkFrame(metrics_row, fg_color=theme.SURFACE_LOW,
                                  corner_radius=theme.CORNER_RADIUS)
        dso_frame.grid(row=0, column=0, padx=(0, 4), sticky="nsew")
        ctk.CTkLabel(dso_frame, text="DSO", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=16, pady=(12, 2), anchor="w")
        dso = self.dashboard_svc.get_dso()
        ctk.CTkLabel(dso_frame, text=f"{dso:.0f} Jours", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=16, pady=(0, 12), anchor="w")

        # Top debtors
        self.debtors_grid = DataGrid(self, columns=[
            ("Client", 250), ("Total Du", 150), ("Statut", 120),
        ])
        self.debtors_grid.pack(fill="x", padx=32, pady=(16, 32))
        self._load_debtors()

    def _load_debtors(self):
        debtors = self.dashboard_svc.get_top_debtors()
        rows = []
        for d in debtors:
            rows.append([d["name"], theme.format_fcfa(d["total_due"]), ""])
        self.debtors_grid.set_data(rows, len(rows), 0, 10)

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
```

- [ ] **Step 2: Update app.py to use real views**

In `terminal_prime/app.py`, replace `_create_placeholder_views` to instantiate `DashboardView` for the "dashboard" key while keeping placeholders for the rest. Import `DashboardView` at the top.

```python
# In app.py, add import:
from terminal_prime.views.dashboard_view import DashboardView

# Replace in _create_placeholder_views:
def _create_placeholder_views(self):
    # Dashboard - real view
    self.views["dashboard"] = DashboardView(self.content, self.conn)
    self.views["dashboard"].grid(row=0, column=0, sticky="nsew")
    # Placeholders for others
    for key, label in Sidebar.NAV_ITEMS:
        if key == "dashboard":
            continue
        frame = ctk.CTkFrame(self.content, fg_color=theme.SURFACE, corner_radius=0)
        frame.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(frame, text=label, font=theme.FONT_HEADING,
                     text_color=theme.ON_SURFACE).place(relx=0.5, rely=0.5, anchor="center")
        self.views[key] = frame
```

- [ ] **Step 3: Test manually**

Run: `python -m terminal_prime.main`
Expected: Dashboard shows KPI cards, aging chart, performance metrics, top debtors grid.

- [ ] **Step 4: Commit**

```bash
git add terminal_prime/views/dashboard_view.py terminal_prime/app.py
git commit -m "feat: add dashboard view with KPIs, aging chart, and top debtors"
```

---

### Task 11: Invoices view (with import)

**Files:**
- Create: `terminal_prime/views/invoices_view.py`
- Modify: `terminal_prime/app.py` (wire up)

- [ ] **Step 1: Implement invoices view**

```python
# terminal_prime/views/invoices_view.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
from terminal_prime import theme
from terminal_prime.components.kpi_card import KpiCard
from terminal_prime.components.data_grid import DataGrid
from terminal_prime.components.status_pill import StatusPill
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.database.client_repo import ClientRepo
from terminal_prime.database.affiliate_repo import AffiliateRepo
from terminal_prime.services.import_service import ImportService
from terminal_prime.services.dashboard_service import DashboardService
from datetime import date, timedelta


class InvoicesView(ctk.CTkScrollableFrame):
    PAGE_SIZE = 10

    def __init__(self, parent, conn, on_data_changed=None):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.invoice_repo = InvoiceRepo(conn)
        self.client_repo = ClientRepo(conn)
        self.affiliate_repo = AffiliateRepo(conn)
        self.import_service = ImportService(conn)
        self.dashboard_svc = DashboardService(conn)
        self.on_data_changed = on_data_changed
        self.current_page = 0
        self.filter_status = None
        self.filter_client = None
        self._build_ui()

    def _build_ui(self):
        # Header row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Gestion des Factures", font=theme.FONT_HEADING,
                     text_color=theme.ON_SURFACE).pack(anchor="w")
        ctk.CTkLabel(left, text="Suivi des factures emises et de leur statut",
                     font=theme.FONT_BODY, text_color=theme.ON_SURFACE_VAR).pack(anchor="w")

        kpis = self.dashboard_svc.get_kpis()
        self.kpi = KpiCard(header, "Total Encours",
                           theme.format_fcfa(kpis["outstanding"]),
                           value_color=theme.PRIMARY)
        self.kpi.grid(row=0, column=1, sticky="e")

        # Filters + actions
        filter_bar = ctk.CTkFrame(self, fg_color=theme.SURFACE_HIGH,
                                   corner_radius=theme.CORNER_RADIUS)
        filter_bar.pack(fill="x", padx=32, pady=(0, 16))

        filters_left = ctk.CTkFrame(filter_bar, fg_color="transparent")
        filters_left.pack(side="left", padx=16, pady=12)

        ctk.CTkLabel(filters_left, text="STATUT", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(side="left", padx=(0, 4))
        self.status_dropdown = ctk.CTkOptionMenu(
            filters_left, values=["Tous", "EN_ATTENTE", "PARTIELLE", "PAYEE", "EN_RETARD"],
            width=140, fg_color=theme.SURFACE_LOWEST,
            button_color=theme.SURFACE_HIGH,
            corner_radius=theme.CORNER_RADIUS,
            command=self._on_filter_status
        )
        self.status_dropdown.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(filters_left, text="CLIENT", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(side="left", padx=(0, 4))
        clients = ["Tous"] + [c.name for c in self.client_repo.get_all()]
        self.client_dropdown = ctk.CTkOptionMenu(
            filters_left, values=clients, width=180,
            fg_color=theme.SURFACE_LOWEST, button_color=theme.SURFACE_HIGH,
            corner_radius=theme.CORNER_RADIUS,
            command=self._on_filter_client
        )
        self.client_dropdown.pack(side="left")

        btns_right = ctk.CTkFrame(filter_bar, fg_color="transparent")
        btns_right.pack(side="right", padx=16, pady=12)

        ctk.CTkButton(btns_right, text="Importer Mediciel",
                      fg_color=theme.SURFACE_HIGHEST,
                      hover_color=theme.SURFACE_BRIGHT,
                      corner_radius=theme.CORNER_RADIUS,
                      command=self._import_mediciel).pack(side="left", padx=4)

        ctk.CTkButton(btns_right, text="Nouvelle Facture",
                      fg_color=theme.PRIMARY_CONT,
                      hover_color=theme.PRIMARY,
                      text_color="white",
                      corner_radius=theme.CORNER_RADIUS,
                      command=self._new_invoice).pack(side="left", padx=4)

        # Data grid
        self.grid_widget = DataGrid(self, columns=[
            ("N. Facture", 160), ("Date", 100), ("Client", 150),
            ("Affilie", 150), ("Montant", 120), ("Solde", 100), ("Statut", 100),
        ], on_page_change=self._on_page_change)
        self.grid_widget.pack(fill="both", padx=32, pady=(0, 32), expand=True)

        self._load_data()

    def _load_data(self):
        status = self.filter_status if self.filter_status != "Tous" else None
        client_id = self.filter_client
        invoices, total = self.invoice_repo.get_all(
            status=status, client_id=client_id,
            limit=self.PAGE_SIZE, offset=self.current_page * self.PAGE_SIZE
        )
        rows = []
        for inv in invoices:
            rows.append([
                inv.number,
                inv.date.strftime("%d/%m/%Y"),
                inv.client_name or "",
                inv.affiliate_name or "",
                theme.format_fcfa(inv.amount),
                theme.format_fcfa(inv.remaining),
                inv.display_status(),
            ])
        self.grid_widget.set_data(rows, total, self.current_page, self.PAGE_SIZE)

    def _on_filter_status(self, value):
        self.filter_status = value if value != "Tous" else None
        self.current_page = 0
        self._load_data()

    def _on_filter_client(self, value):
        if value == "Tous":
            self.filter_client = None
        else:
            clients = self.client_repo.search(value)
            self.filter_client = clients[0].id if clients else None
        self.current_page = 0
        self._load_data()

    def _on_page_change(self, page):
        self.current_page = page
        self._load_data()

    def _import_mediciel(self):
        filepath = filedialog.askopenfilename(
            title="Selectionner l'export Mediciel",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            result = self.import_service.import_file(filepath)
            msg = (f"Import termine !\n\n"
                   f"Factures importees : {result['imported']}\n"
                   f"Doublons ignores : {result['duplicates']}\n"
                   f"Clients crees : {result['clients_created']}\n"
                   f"Affilies crees : {result['affiliates_created']}")
            if result['errors'] > 0:
                msg += f"\nErreurs : {result['errors']}"
            messagebox.showinfo("Import Mediciel", msg)
            self.refresh()
            if self.on_data_changed:
                self.on_data_changed()
        except Exception as e:
            messagebox.showerror("Erreur d'import", str(e))

    def _new_invoice(self):
        InvoiceModal(self, self.conn, on_save=lambda: (self.refresh(),
                     self.on_data_changed() if self.on_data_changed else None))

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()


class InvoiceModal(ctk.CTkToplevel):
    def __init__(self, parent, conn, on_save=None):
        super().__init__(parent)
        self.title("Nouvelle Facture")
        self.geometry("500x400")
        self.configure(fg_color=theme.SURFACE_BRIGHT)
        self.conn = conn
        self.on_save = on_save
        self.client_repo = ClientRepo(conn)
        self.affiliate_repo = AffiliateRepo(conn)
        self.invoice_repo = InvoiceRepo(conn)

        self.grab_set()
        self._build_form()

    def _build_form(self):
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(form, text="Nouvelle Facture", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(pady=(0, 20), anchor="w")

        # Number
        ctk.CTkLabel(form, text="N. FACTURE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(anchor="w")
        self.number_entry = ctk.CTkEntry(form, fg_color=theme.SURFACE_LOWEST,
                                          border_width=0, corner_radius=theme.CORNER_RADIUS)
        self.number_entry.pack(fill="x", pady=(2, 12))

        # Client
        ctk.CTkLabel(form, text="CLIENT PRINCIPAL", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(anchor="w")
        clients = [c.name for c in self.client_repo.get_all()]
        self.client_var = ctk.StringVar()
        self.client_menu = ctk.CTkOptionMenu(form, values=clients or ["(aucun)"],
                                              variable=self.client_var,
                                              fg_color=theme.SURFACE_LOWEST,
                                              corner_radius=theme.CORNER_RADIUS,
                                              command=self._on_client_change)
        self.client_menu.pack(fill="x", pady=(2, 12))

        # Affiliate
        ctk.CTkLabel(form, text="AFFILIE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(anchor="w")
        self.aff_var = ctk.StringVar()
        self.aff_menu = ctk.CTkOptionMenu(form, values=["(selectionner client)"],
                                           variable=self.aff_var,
                                           fg_color=theme.SURFACE_LOWEST,
                                           corner_radius=theme.CORNER_RADIUS)
        self.aff_menu.pack(fill="x", pady=(2, 12))

        # Amount
        ctk.CTkLabel(form, text="MONTANT (FCFA)", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(anchor="w")
        self.amount_entry = ctk.CTkEntry(form, fg_color=theme.SURFACE_LOWEST,
                                          border_width=0, corner_radius=theme.CORNER_RADIUS,
                                          placeholder_text="0")
        self.amount_entry.pack(fill="x", pady=(2, 20))

        # Save button
        ctk.CTkButton(form, text="Enregistrer", fg_color=theme.PRIMARY_CONT,
                      hover_color=theme.PRIMARY, text_color="white",
                      corner_radius=theme.CORNER_RADIUS,
                      command=self._save).pack(fill="x")

    def _on_client_change(self, client_name):
        clients = self.client_repo.search(client_name)
        if clients:
            affs = self.affiliate_repo.get_by_client(clients[0].id)
            aff_names = [a.name for a in affs] or ["(aucun)"]
            self.aff_menu.configure(values=aff_names)
            self.aff_var.set(aff_names[0])

    def _save(self):
        number = self.number_entry.get().strip()
        client_name = self.client_var.get()
        aff_name = self.aff_var.get()
        amount_str = self.amount_entry.get().strip()

        if not number or not client_name or not amount_str:
            messagebox.showwarning("Champs requis", "Veuillez remplir tous les champs obligatoires.")
            return

        try:
            amount = int(amount_str)
        except ValueError:
            messagebox.showwarning("Montant invalide", "Le montant doit etre un nombre entier.")
            return

        client_id = self.client_repo.get_or_create(client_name)
        aff_id = self.affiliate_repo.get_or_create(aff_name, client_id)
        today = date.today()
        due = today + timedelta(days=30)

        try:
            self.invoice_repo.create(number, client_id, aff_id, today, due, amount)
            if self.on_save:
                self.on_save()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
```

- [ ] **Step 2: Wire up in app.py**

Add `InvoicesView` import and replace the "invoices" placeholder in `_create_placeholder_views`:

```python
from terminal_prime.views.invoices_view import InvoicesView

# In _create_placeholder_views, replace invoices placeholder:
self.views["invoices"] = InvoicesView(self.content, self.conn,
                                      on_data_changed=self._refresh_all)
self.views["invoices"].grid(row=0, column=0, sticky="nsew")

# Add refresh method:
def _refresh_all(self):
    for view in self.views.values():
        if hasattr(view, 'refresh'):
            view.refresh()
```

- [ ] **Step 3: Test manually**

Run: `python -m terminal_prime.main`
Expected: Invoices screen with import button, filters, data grid. Import the Mediciel file.

- [ ] **Step 4: Commit**

```bash
git add terminal_prime/views/invoices_view.py terminal_prime/app.py
git commit -m "feat: add invoices view with Mediciel import and manual creation"
```

---

### Task 12: Collections view

**Files:**
- Create: `terminal_prime/views/collections_view.py`
- Modify: `terminal_prime/app.py`

- [ ] **Step 1: Implement collections view**

```python
# terminal_prime/views/collections_view.py
import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from terminal_prime import theme
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.database.payment_repo import PaymentRepo
from terminal_prime.services.dashboard_service import DashboardService
from terminal_prime.models.payment import PaymentMode


class CollectionsView(ctk.CTkScrollableFrame):
    def __init__(self, parent, conn, on_data_changed=None):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.invoice_repo = InvoiceRepo(conn)
        self.payment_repo = PaymentRepo(conn)
        self.dashboard_svc = DashboardService(conn)
        self.on_data_changed = on_data_changed
        self._build_ui()

    def _build_ui(self):
        # Header
        ctk.CTkLabel(self, text="Gestion des Recouvrements", font=theme.FONT_HEADING,
                     text_color=theme.ON_SURFACE).pack(padx=32, pady=(32, 4), anchor="w")
        ctk.CTkLabel(self, text="Saisie et suivi des paiements recus",
                     font=theme.FONT_BODY, text_color=theme.ON_SURFACE_VAR).pack(
            padx=32, pady=(0, 24), anchor="w")

        # Main content: form left, recent right
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", padx=32, pady=(0, 16), expand=True)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        # Payment form
        form_frame = ctk.CTkFrame(content, fg_color=theme.SURFACE_CONT,
                                   corner_radius=theme.CORNER_RADIUS)
        form_frame.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ctk.CTkLabel(form_frame, text="Saisie de Paiement", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(20, 16), anchor="w")

        # Invoice selection
        ctk.CTkLabel(form_frame, text="FACTURE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, anchor="w")
        unpaid = self.invoice_repo.get_unpaid()
        inv_labels = [f"{i.number} - {i.client_name} ({theme.format_fcfa(i.remaining)})"
                      for i in unpaid]
        self._unpaid_invoices = unpaid
        self.inv_var = ctk.StringVar()
        self.inv_menu = ctk.CTkOptionMenu(
            form_frame, values=inv_labels or ["(aucune facture)"],
            variable=self.inv_var,
            fg_color=theme.SURFACE_LOWEST, corner_radius=theme.CORNER_RADIUS,
            command=self._on_invoice_select
        )
        self.inv_menu.pack(fill="x", padx=24, pady=(2, 12))

        # Date
        ctk.CTkLabel(form_frame, text="DATE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, anchor="w")
        self.date_entry = ctk.CTkEntry(form_frame, fg_color=theme.SURFACE_LOWEST,
                                        border_width=0, corner_radius=theme.CORNER_RADIUS)
        self.date_entry.insert(0, date.today().strftime("%d/%m/%Y"))
        self.date_entry.pack(fill="x", padx=24, pady=(2, 12))

        # Mode
        ctk.CTkLabel(form_frame, text="MODE", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, anchor="w")
        self.mode_var = ctk.StringVar(value="VIREMENT")
        ctk.CTkOptionMenu(form_frame, values=["VIREMENT", "CHEQUE", "ESPECES"],
                          variable=self.mode_var,
                          fg_color=theme.SURFACE_LOWEST,
                          corner_radius=theme.CORNER_RADIUS).pack(
            fill="x", padx=24, pady=(2, 12))

        # Amount
        ctk.CTkLabel(form_frame, text="MONTANT (FCFA)", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=24, anchor="w")
        self.amount_entry = ctk.CTkEntry(form_frame, fg_color=theme.SURFACE_LOWEST,
                                          border_width=0, corner_radius=theme.CORNER_RADIUS,
                                          placeholder_text="0")
        self.amount_entry.pack(fill="x", padx=24, pady=(2, 20))

        # Save
        ctk.CTkButton(form_frame, text="Valider le paiement",
                      fg_color=theme.PRIMARY_CONT, hover_color=theme.PRIMARY,
                      text_color="white", corner_radius=theme.CORNER_RADIUS,
                      command=self._save_payment).pack(fill="x", padx=24, pady=(0, 24))

        # Recent payments
        recent_frame = ctk.CTkFrame(content, fg_color=theme.SURFACE_CONT,
                                     corner_radius=theme.CORNER_RADIUS)
        recent_frame.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ctk.CTkLabel(recent_frame, text="Derniers Recouvrements", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(20, 16), anchor="w")
        self._load_recent(recent_frame)

        # Stats bar
        stats = ctk.CTkFrame(self, fg_color=theme.SURFACE_CONT,
                              corner_radius=theme.CORNER_RADIUS)
        stats.pack(fill="x", padx=32, pady=(16, 32))
        stats.grid_columnconfigure((0, 1, 2), weight=1, uniform="stat")

        mtd = self.payment_repo.get_total_collected_mtd()
        kpis = self.dashboard_svc.get_kpis()
        dso = self.dashboard_svc.get_dso()

        for col, (label, val) in enumerate([
            ("Total Collecte (Mois)", theme.format_fcfa(mtd)),
            ("Encours Restant", theme.format_fcfa(kpis["outstanding"])),
            ("DSO", f"{dso:.0f} Jours"),
        ]):
            f = ctk.CTkFrame(stats, fg_color="transparent")
            f.grid(row=0, column=col, padx=24, pady=16)
            ctk.CTkLabel(f, text=label.upper(), font=theme.FONT_LABEL_UPPER,
                         text_color=theme.ON_SURFACE_VAR).pack(anchor="w")
            ctk.CTkLabel(f, text=val, font=theme.FONT_TITLE,
                         text_color=theme.ON_SURFACE).pack(anchor="w")

    def _on_invoice_select(self, value):
        # Auto-fill max amount
        idx = self.inv_menu.cget("values").index(value) if value in self.inv_menu.cget("values") else -1
        if 0 <= idx < len(self._unpaid_invoices):
            inv = self._unpaid_invoices[idx]
            self.amount_entry.delete(0, "end")
            self.amount_entry.insert(0, str(inv.remaining))

    def _save_payment(self):
        inv_label = self.inv_var.get()
        amount_str = self.amount_entry.get().strip()
        date_str = self.date_entry.get().strip()

        if not inv_label or not amount_str:
            messagebox.showwarning("Champs requis", "Veuillez selectionner une facture et saisir un montant.")
            return

        try:
            amount = int(amount_str)
        except ValueError:
            messagebox.showwarning("Montant invalide", "Le montant doit etre un nombre entier.")
            return

        # Find selected invoice
        idx = -1
        values = self.inv_menu.cget("values") if hasattr(self.inv_menu, "cget") else []
        for i, v in enumerate(values):
            if v == inv_label:
                idx = i
                break
        if idx < 0 or idx >= len(self._unpaid_invoices):
            messagebox.showwarning("Erreur", "Facture non trouvee.")
            return

        inv = self._unpaid_invoices[idx]
        if amount > inv.remaining:
            messagebox.showwarning("Montant excessif",
                                    f"Le montant ne peut pas depasser le solde restant ({theme.format_fcfa(inv.remaining)}).")
            return

        try:
            parts = date_str.split("/")
            pay_date = date(int(parts[2]), int(parts[1]), int(parts[0]))
        except (ValueError, IndexError):
            messagebox.showwarning("Date invalide", "Format attendu : JJ/MM/AAAA")
            return

        mode = PaymentMode(self.mode_var.get())
        self.payment_repo.create(inv.id, inv.client_id, pay_date, amount, mode)
        self.invoice_repo.update_status_from_payments(inv.id)

        messagebox.showinfo("Paiement enregistre",
                            f"Paiement de {theme.format_fcfa(amount)} enregistre pour {inv.number}.")
        self.refresh()
        if self.on_data_changed:
            self.on_data_changed()

    def _load_recent(self, parent):
        payments = self.payment_repo.get_recent(5)
        for p in payments:
            row = ctk.CTkFrame(parent, fg_color=theme.SURFACE_LOW,
                               corner_radius=theme.CORNER_RADIUS)
            row.pack(fill="x", padx=16, pady=4)
            ctk.CTkLabel(row, text=p.reference or "", font=theme.FONT_BODY_BOLD,
                         text_color=theme.ON_SURFACE).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(row, text=theme.format_fcfa(p.amount), font=theme.FONT_BODY,
                         text_color=theme.TERTIARY).pack(side="right", padx=12, pady=8)

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
```

- [ ] **Step 2: Wire up in app.py**

```python
from terminal_prime.views.collections_view import CollectionsView

# Replace collections placeholder:
self.views["collections"] = CollectionsView(self.content, self.conn,
                                             on_data_changed=self._refresh_all)
self.views["collections"].grid(row=0, column=0, sticky="nsew")
```

- [ ] **Step 3: Test manually**

Run: `python -m terminal_prime.main`
Expected: Collections screen with payment form, recent payments list, stats bar.

- [ ] **Step 4: Commit**

```bash
git add terminal_prime/views/collections_view.py terminal_prime/app.py
git commit -m "feat: add collections view with payment entry and recent payments"
```

---

### Task 13: Client analysis view

**Files:**
- Create: `terminal_prime/views/client_analysis_view.py`
- Modify: `terminal_prime/app.py`

- [ ] **Step 1: Implement client analysis view**

```python
# terminal_prime/views/client_analysis_view.py
import customtkinter as ctk
from terminal_prime import theme
from terminal_prime.components.kpi_card import KpiCard
from terminal_prime.components.bar_chart import BarChart
from terminal_prime.database.client_repo import ClientRepo
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.services.aging_service import AgingService
from datetime import date, timedelta


class ClientAnalysisView(ctk.CTkScrollableFrame):
    def __init__(self, parent, conn):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.client_repo = ClientRepo(conn)
        self.invoice_repo = InvoiceRepo(conn)
        self.aging_svc = AgingService(conn)
        self.selected_client = None
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(32, 16))
        ctk.CTkLabel(header, text="Analyse Client", font=theme.FONT_HEADING,
                     text_color=theme.ON_SURFACE).pack(side="left")

        # Client search/select
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=32, pady=(0, 16))

        ctk.CTkLabel(search_frame, text="SELECTIONNER UN CLIENT", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(side="left", padx=(0, 8))
        clients = self.client_repo.get_all()
        client_names = [c.name for c in clients]
        self._clients = clients
        self.client_var = ctk.StringVar()
        ctk.CTkOptionMenu(search_frame, values=client_names or ["(aucun client)"],
                          variable=self.client_var,
                          fg_color=theme.SURFACE_LOWEST,
                          corner_radius=theme.CORNER_RADIUS,
                          command=self._on_client_select).pack(side="left")

        # Detail container (empty until client selected)
        self.detail_container = ctk.CTkFrame(self, fg_color="transparent")
        self.detail_container.pack(fill="both", expand=True, padx=32, pady=(0, 32))

        if clients:
            self.client_var.set(clients[0].name)
            self._on_client_select(clients[0].name)

    def _on_client_select(self, name):
        client = next((c for c in self._clients if c.name == name), None)
        if not client:
            return
        self.selected_client = client

        for widget in self.detail_container.winfo_children():
            widget.destroy()

        # Client header
        ctk.CTkLabel(self.detail_container, text=client.name,
                     font=theme.FONT_HEADING,
                     text_color=theme.ON_SURFACE).pack(anchor="w", pady=(0, 16))

        # Aging breakdown
        aging = self.aging_svc.get_client_aging(client.id)
        total = sum(aging.values())

        # KPI row
        kpi_row = ctk.CTkFrame(self.detail_container, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 16))
        kpi_row.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="aging")

        labels = [("Courant", "current"), ("0-30j", "0-30"), ("31-60j", "31-60"),
                  ("61-90j", "61-90"), ("90+j", "90+")]
        colors = [theme.PRIMARY, theme.PRIMARY, theme.TERTIARY,
                  theme.TERTIARY_CONT, theme.ERROR]
        for col, ((label, key), color) in enumerate(zip(labels, colors)):
            f = ctk.CTkFrame(kpi_row, fg_color=theme.SURFACE_CONT,
                             corner_radius=theme.CORNER_RADIUS)
            f.grid(row=0, column=col, padx=4, sticky="nsew")
            ctk.CTkLabel(f, text=label.upper(), font=theme.FONT_LABEL_UPPER,
                         text_color=theme.ON_SURFACE_VAR).pack(padx=16, pady=(12, 2), anchor="w")
            ctk.CTkLabel(f, text=theme.format_fcfa(aging.get(key, 0)),
                         font=theme.FONT_TITLE, text_color=color).pack(
                padx=16, pady=(0, 12), anchor="w")

        # Solde total
        KpiCard(self.detail_container, "Solde Total",
                theme.format_fcfa(total),
                value_color=theme.ERROR if total > 0 else theme.TERTIARY).pack(
            fill="x", pady=(0, 16))

        # Timeline chart
        self.timeline = BarChart(self.detail_container,
                                 "Timeline : Factures vs Paiements",
                                 "6 derniers mois")
        self.timeline.pack(fill="x", pady=(0, 16))
        self.after(200, lambda: self._load_timeline(client.id))

    def _load_timeline(self, client_id):
        today = date.today()
        bars = []
        for i in range(5, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1)
            label = month_start.strftime("%b")

            invoiced = self.conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE client_id = ? AND date >= ? AND date < ?",
                (client_id, str(month_start), str(month_end))
            ).fetchone()[0]

            paid = self.conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE client_id = ? AND date >= ? AND date < ?",
                (client_id, str(month_start), str(month_end))
            ).fetchone()[0]

            bars.append((label, invoiced, theme.PRIMARY))

        self.timeline.set_data(bars)

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
```

- [ ] **Step 2: Wire up in app.py, test, commit**

```python
from terminal_prime.views.client_analysis_view import ClientAnalysisView
self.views["analysis"] = ClientAnalysisView(self.content, self.conn)
self.views["analysis"].grid(row=0, column=0, sticky="nsew")
```

Run: `python -m terminal_prime.main`

```bash
git add terminal_prime/views/client_analysis_view.py terminal_prime/app.py
git commit -m "feat: add client analysis view with aging breakdown and timeline"
```

---

### Task 14: Reports view

**Files:**
- Create: `terminal_prime/views/reports_view.py`
- Create: `terminal_prime/services/export_service.py`
- Modify: `terminal_prime/app.py`

- [ ] **Step 1: Implement export service**

```python
# terminal_prime/services/export_service.py
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import date
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.services.aging_service import AgingService


class ExportService:
    def __init__(self, conn):
        self.conn = conn
        self.invoice_repo = InvoiceRepo(conn)
        self.aging_svc = AgingService(conn)

    def export_aging_excel(self, filepath: str):
        wb = Workbook()
        ws = wb.active
        ws.title = "Balance Agee"

        # Header style
        header_font = Font(name="Inter", bold=True, size=10, color="FFFFFF")
        header_fill = PatternFill(start_color="1f538d", end_color="1f538d", fill_type="solid")

        headers = ["N. Facture", "Date", "Echeance", "Client", "Affilie",
                   "Montant", "Paye", "Solde", "Jours Retard", "Statut"]
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

        invoices, _ = self.invoice_repo.get_all(limit=99999)
        today = date.today()
        for row_idx, inv in enumerate(invoices, 2):
            days_overdue = max(0, (today - inv.due_date).days)
            ws.cell(row=row_idx, column=1, value=inv.number)
            ws.cell(row=row_idx, column=2, value=inv.date.strftime("%d/%m/%Y"))
            ws.cell(row=row_idx, column=3, value=inv.due_date.strftime("%d/%m/%Y"))
            ws.cell(row=row_idx, column=4, value=inv.client_name)
            ws.cell(row=row_idx, column=5, value=inv.affiliate_name)
            ws.cell(row=row_idx, column=6, value=inv.amount)
            ws.cell(row=row_idx, column=7, value=inv.total_paid)
            ws.cell(row=row_idx, column=8, value=inv.remaining)
            ws.cell(row=row_idx, column=9, value=days_overdue)
            ws.cell(row=row_idx, column=10, value=inv.display_status())

        # Auto column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 30)

        wb.save(filepath)
```

- [ ] **Step 2: Implement reports view**

```python
# terminal_prime/views/reports_view.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import date
from terminal_prime import theme
from terminal_prime.components.kpi_card import KpiCard
from terminal_prime.components.data_grid import DataGrid
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.services.dashboard_service import DashboardService
from terminal_prime.services.aging_service import AgingService
from terminal_prime.services.export_service import ExportService


class ReportsView(ctk.CTkScrollableFrame):
    def __init__(self, parent, conn):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.invoice_repo = InvoiceRepo(conn)
        self.dashboard_svc = DashboardService(conn)
        self.aging_svc = AgingService(conn)
        self.export_svc = ExportService(conn)
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(32, 16))
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="Rapports & Relances", font=theme.FONT_HEADING,
                     text_color=theme.ON_SURFACE).pack(anchor="w")
        ctk.CTkLabel(left, text="Analyse du recouvrement et de la balance agee",
                     font=theme.FONT_BODY, text_color=theme.ON_SURFACE_VAR).pack(anchor="w")

        # Export button
        ctk.CTkButton(header, text="Export Balance Agee (Excel)",
                      fg_color=theme.PRIMARY_CONT, hover_color=theme.PRIMARY,
                      text_color="white", corner_radius=theme.CORNER_RADIUS,
                      command=self._export_excel).pack(side="right")

        # KPIs
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", padx=32, pady=(0, 16))
        kpi_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="kpi")

        kpis = self.dashboard_svc.get_kpis()
        buckets = self.aging_svc.get_aging_buckets()
        overdue_30 = buckets["31-60"] + buckets["61-90"] + buckets["90+"]
        overdue_90 = buckets["90+"]

        KpiCard(kpi_row, "Encours Total Echu",
                theme.format_fcfa(kpis["outstanding"]),
                value_color=theme.ERROR).grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        KpiCard(kpi_row, "Retards > 30j",
                theme.format_fcfa(overdue_30),
                value_color=theme.TERTIARY).grid(row=0, column=1, padx=8, sticky="nsew")
        KpiCard(kpi_row, "Retards > 90j",
                theme.format_fcfa(overdue_90),
                value_color=theme.ERROR).grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        # Overdue invoices table
        ctk.CTkLabel(self, text="FACTURES ECHUES", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=32, pady=(16, 8), anchor="w")

        self.grid_widget = DataGrid(self, columns=[
            ("N. Facture", 160), ("Client", 150), ("Montant", 120),
            ("Echeance", 100), ("Retard", 80), ("Statut", 100),
        ])
        self.grid_widget.pack(fill="both", padx=32, pady=(0, 16), expand=True)
        self._load_overdue()

        # DSO
        dso = self.dashboard_svc.get_dso()
        dso_frame = ctk.CTkFrame(self, fg_color=theme.SURFACE_CONT,
                                  corner_radius=theme.CORNER_RADIUS)
        dso_frame.pack(fill="x", padx=32, pady=(0, 32))
        dso_inner = ctk.CTkFrame(dso_frame, fg_color="transparent")
        dso_inner.pack(padx=24, pady=16)
        ctk.CTkLabel(dso_inner, text="DELAI DE PAIEMENT MOYEN (DSO)",
                     font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(side="left", padx=(0, 16))
        ctk.CTkLabel(dso_inner, text=f"{dso:.0f} Jours", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(side="left")

    def _load_overdue(self):
        invoices = self.invoice_repo.get_unpaid()
        today = date.today()
        overdue = [inv for inv in invoices if inv.is_overdue(today)]
        overdue.sort(key=lambda i: (today - i.due_date).days, reverse=True)

        rows = []
        for inv in overdue[:50]:
            days = (today - inv.due_date).days
            rows.append([
                inv.number,
                inv.client_name or "",
                theme.format_fcfa(inv.remaining),
                inv.due_date.strftime("%d/%m/%Y"),
                f"{days}j",
                inv.display_status(),
            ])
        self.grid_widget.set_data(rows, len(rows), 0, 50)

    def _export_excel(self):
        filepath = filedialog.asksaveasfilename(
            title="Exporter la Balance Agee",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile=f"balance_agee_{date.today().strftime('%Y%m%d')}.xlsx"
        )
        if not filepath:
            return
        try:
            self.export_svc.export_aging_excel(filepath)
            messagebox.showinfo("Export", f"Balance agee exportee vers :\n{filepath}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
```

- [ ] **Step 3: Wire up in app.py, test, commit**

```python
from terminal_prime.views.reports_view import ReportsView
self.views["reports"] = ReportsView(self.content, self.conn)
self.views["reports"].grid(row=0, column=0, sticky="nsew")
```

Run: `python -m terminal_prime.main`

```bash
git add terminal_prime/views/reports_view.py terminal_prime/services/export_service.py terminal_prime/app.py
git commit -m "feat: add reports view with overdue table and Excel export"
```

---

### Task 15: Final app.py integration and polish

**Files:**
- Modify: `terminal_prime/app.py`

- [ ] **Step 1: Wire up all views in app.py**

Replace `_create_placeholder_views` with all real views and add `_refresh_all`:

```python
def _create_placeholder_views(self):
    self.views["dashboard"] = DashboardView(self.content, self.conn)
    self.views["invoices"] = InvoicesView(self.content, self.conn,
                                          on_data_changed=self._refresh_all)
    self.views["collections"] = CollectionsView(self.content, self.conn,
                                                 on_data_changed=self._refresh_all)
    self.views["analysis"] = ClientAnalysisView(self.content, self.conn)
    self.views["reports"] = ReportsView(self.content, self.conn)
    for view in self.views.values():
        view.grid(row=0, column=0, sticky="nsew")

def _navigate(self, key: str):
    for view in self.views.values():
        view.grid_remove()
    self.views[key].grid()
    if hasattr(self.views[key], 'refresh'):
        self.views[key].refresh()

def _refresh_all(self):
    for view in self.views.values():
        if hasattr(view, 'refresh'):
            view.refresh()
```

- [ ] **Step 2: Full manual test**

Run: `python -m terminal_prime.main`
Test: Navigate all 5 screens, import Mediciel file, add payment, check dashboard updates, export Excel.

- [ ] **Step 3: Commit**

```bash
git add terminal_prime/app.py
git commit -m "feat: wire up all views and add cross-screen refresh"
```

---

---

## Chunk 4: Review Fixes

### Task 16: Fix DB connection for test isolation

**Files:**
- Modify: `terminal_prime/database/connection.py`

- [ ] **Step 1: Fix get_connection to accept existing connection**

The singleton should not cache by path. Tests pass `conn` directly to repos/services, so the singleton is only used by `app.py`. No change needed to test fixtures — they already create and pass their own connections. But ensure `close_connection()` properly resets state.

---

### Task 17: Fix aging bucket consistency

**Files:**
- Modify: `terminal_prime/services/aging_service.py`

- [ ] **Step 1: Add "current" bucket to get_aging_buckets**

Both `get_aging_buckets` and `get_client_aging` should return the same bucket structure: `{"current", "0-30", "31-60", "61-90", "90+"}`. "current" = not yet due, "0-30" = 1-30 days overdue.

- [ ] **Step 2: Update dashboard_view.py to handle "current" bucket**

- [ ] **Step 3: Update tests accordingly**

---

### Task 18: Fix DataGrid status pill rendering

**Files:**
- Modify: `terminal_prime/components/data_grid.py`

- [ ] **Step 1: Pass status as string, create StatusPill inside DataGrid**

Instead of receiving widget objects, `set_data` receives plain strings. For columns that need a StatusPill, add a `status_columns` parameter (set of column indices). The DataGrid creates the StatusPill internally with the correct parent.

---

### Task 19: Fix DSO query

**Files:**
- Modify: `terminal_prime/services/dashboard_service.py`

- [ ] **Step 1: Use correlated subquery for outstanding calculation**

```python
def get_dso(self) -> float:
    today = date.today()
    start = today - timedelta(days=90)
    outstanding = self.conn.execute(
        """SELECT COALESCE(SUM(i.amount -
              COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0)
           ), 0)
           FROM invoices i WHERE i.status != 'PAYEE'"""
    ).fetchone()[0]
    credit_sales = self.conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE date >= ?",
        (str(start),)
    ).fetchone()[0]
    if credit_sales == 0:
        return 0.0
    return (outstanding / credit_sales) * 90
```

---

### Task 20: Add CEI calculation

**Files:**
- Modify: `terminal_prime/services/dashboard_service.py`
- Modify: `terminal_prime/views/dashboard_view.py`

- [ ] **Step 1: Add get_cei method**

```python
def get_cei(self) -> float:
    today = date.today()
    first_of_month = today.replace(day=1)
    if first_of_month.month == 1:
        prev_month = first_of_month.replace(year=first_of_month.year - 1, month=12)
    else:
        prev_month = first_of_month.replace(month=first_of_month.month - 1)

    recv_start = self.conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE status != 'PAYEE' AND date < ?",
        (str(first_of_month),)
    ).fetchone()[0]
    facturations = self.conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM invoices WHERE date >= ?",
        (str(first_of_month),)
    ).fetchone()[0]
    recv_end = self.conn.execute(
        "SELECT COALESCE(SUM(i.amount - COALESCE((SELECT SUM(p.amount) FROM payments p WHERE p.invoice_id = i.id), 0)), 0) FROM invoices i WHERE i.status != 'PAYEE'"
    ).fetchone()[0]

    denom = recv_start + facturations
    if denom == 0:
        return 0.0
    return ((recv_start + facturations - recv_end) / denom) * 100
```

- [ ] **Step 2: Display CEI in dashboard view alongside DSO**

---

### Task 21: Add PDF export

**Files:**
- Modify: `terminal_prime/services/export_service.py`
- Create: `tests/test_export_service.py`

- [ ] **Step 1: Write tests for Excel and PDF export**

```python
# tests/test_export_service.py
import os
import tempfile
from datetime import date
from terminal_prime.database.connection import get_connection, close_connection
from terminal_prime.database.schema import create_tables
from terminal_prime.database.client_repo import ClientRepo
from terminal_prime.database.affiliate_repo import AffiliateRepo
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.services.export_service import ExportService
import pytest


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    conn = get_connection(db_path)
    create_tables(conn)
    cr = ClientRepo(conn)
    ar = AffiliateRepo(conn)
    ir = InvoiceRepo(conn)
    cid = cr.create("ASSUREUR TEST")
    aid = ar.create("AFFILIE TEST", cid)
    ir.create("EXP-001", cid, aid, date(2025, 1, 1), date(2025, 1, 31), 100000)
    ir.create("EXP-002", cid, aid, date(2025, 2, 1), date(2025, 3, 3), 200000)
    yield conn
    close_connection()
    os.unlink(db_path)


def test_export_excel(db):
    svc = ExportService(db)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        path = f.name
    try:
        svc.export_aging_excel(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_export_invoice_pdf(db):
    svc = ExportService(db)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        svc.export_invoice_pdf(1, path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)
```

- [ ] **Step 2: Add PDF generation method**

```python
# Add to terminal_prime/services/export_service.py

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from terminal_prime.database.payment_repo import PaymentRepo


def export_invoice_pdf(self, invoice_id: int, filepath: str):
    inv = self.invoice_repo.get_by_id(invoice_id)
    if not inv:
        raise ValueError("Facture introuvable")

    payment_repo = PaymentRepo(self.conn)
    payments = payment_repo.get_by_invoice(invoice_id)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Terminal Prime", styles["Title"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Facture N. {inv.number}", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    info = [
        ["Client:", inv.client_name or ""],
        ["Affilie:", inv.affiliate_name or ""],
        ["Date:", inv.date.strftime("%d/%m/%Y")],
        ["Echeance:", inv.due_date.strftime("%d/%m/%Y")],
        ["Montant:", f"{inv.amount:,} FCFA".replace(",", " ")],
        ["Statut:", inv.display_status()],
    ]
    t = Table(info, colWidths=[120, 300])
    t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 10)]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    if payments:
        elements.append(Paragraph("Paiements", styles["Heading3"]))
        pay_data = [["Reference", "Date", "Mode", "Montant"]]
        for p in payments:
            pay_data.append([
                p.reference or "",
                p.date.strftime("%d/%m/%Y"),
                p.mode.value,
                f"{p.amount:,} FCFA".replace(",", " "),
            ])
        pt = Table(pay_data, colWidths=[120, 100, 100, 120])
        pt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f538d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(pt)

    doc.build(elements)
```

- [ ] **Step 3: Run tests, commit**

---

### Task 22: Add period filter to invoices view

**Files:**
- Modify: `terminal_prime/views/invoices_view.py`
- Modify: `terminal_prime/database/invoice_repo.py`

- [ ] **Step 1: Add date range filter to InvoiceRepo.get_all()**

Add optional `date_from` and `date_to` parameters.

- [ ] **Step 2: Add period dropdown to invoices view filter bar**

Values: "Tous", "Mois en cours", "Dernier trimestre", "Annee en cours"

---

### Task 23: Fix month arithmetic in client analysis timeline

**Files:**
- Modify: `terminal_prime/views/client_analysis_view.py`

- [ ] **Step 1: Use proper month subtraction**

```python
def _month_subtract(self, d: date, months: int) -> date:
    month = d.month - months
    year = d.year
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, 1)
```

---

### Task 24: Remove KpiCard.update_values()

**Files:**
- Modify: `terminal_prime/components/kpi_card.py`

- [ ] **Step 1: Delete the broken update_values method**

Views already use `refresh()` to rebuild entirely.

---

### Task 25: Run all tests and final commit

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: ALL PASS

- [ ] **Step 2: Final commit**

```bash
git add -A
git commit -m "chore: complete Terminal Prime v1 - balance commerciale agee"
```
