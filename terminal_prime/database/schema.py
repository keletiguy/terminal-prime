import sqlite3


def create_tables(conn: sqlite3.Connection) -> None:
    """Create all application tables if they don't exist."""
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
            client_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, client_id),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL UNIQUE,
            client_id INTEGER NOT NULL,
            affiliate_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            amount INTEGER NOT NULL,
            status TEXT DEFAULT 'EN_ATTENTE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id),
            FOREIGN KEY (affiliate_id) REFERENCES affiliates(id)
        );

        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            client_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            amount INTEGER NOT NULL,
            mode TEXT NOT NULL,
            reference TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );
    """)
