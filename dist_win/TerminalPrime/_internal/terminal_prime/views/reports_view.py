"""Reports view with overdue invoices, KPIs, and export functionality."""
import sqlite3
from datetime import date
from tkinter import filedialog, messagebox

import customtkinter as ctk

from terminal_prime import theme
from terminal_prime.components.kpi_card import KpiCard
from terminal_prime.components.data_grid import DataGrid
from terminal_prime.database.invoice_repo import InvoiceRepo
from terminal_prime.services.dashboard_service import DashboardService
from terminal_prime.services.export_service import ExportService


class ReportsView(ctk.CTkScrollableFrame):
    PAGE_SIZE = 10

    def __init__(self, parent, conn: sqlite3.Connection):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.invoice_repo = InvoiceRepo(conn)
        self.dashboard_svc = DashboardService(conn)
        self.export_svc = ExportService(conn)
        self.current_page = 0
        self._build()

    def _build(self):
        today = date.today()

        # ── Header ───────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 16))

        ctk.CTkLabel(header, text="Rapports & Relances", font=theme.FONT_HEADING,
                     text_color=theme.ON_SURFACE).pack(side="left")

        ctk.CTkButton(header, text="Export Excel", fg_color=theme.PRIMARY_CONT,
                      text_color="white", font=theme.FONT_BODY_BOLD, width=140,
                      command=self._export_excel).pack(side="right")

        # ── 3 KPIs ──────────────────────────────────────────────────────
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", padx=24, pady=(0, 16))
        kpi_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="kpi")

        overdue_data = self._get_overdue_stats(today)

        KpiCard(kpi_row, label="Encours Total Echu",
                value=theme.format_fcfa(overdue_data["total_overdue"]),
                value_color=theme.ERROR
                ).grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        KpiCard(kpi_row, label="Retards >30j",
                value=theme.format_fcfa(overdue_data["over_30"]),
                value_color=theme.TERTIARY
                ).grid(row=0, column=1, padx=8, sticky="nsew")

        KpiCard(kpi_row, label="Retards >90j",
                value=theme.format_fcfa(overdue_data["over_90"]),
                value_color=theme.ERROR
                ).grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        # ── Overdue Invoices DataGrid ────────────────────────────────────
        ctk.CTkLabel(self, text="Factures en Retard", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(0, 8), anchor="w")

        self.grid_widget = DataGrid(
            self,
            columns=[("N.Facture", 160), ("Client", 150), ("Montant", 120),
                     ("Echeance", 100), ("Retard", 80), ("Statut", 100)],
            status_columns={5},
            on_page_change=self._on_page_change,
        )
        self.grid_widget.pack(fill="x", padx=24, pady=(0, 16))
        self._load_overdue(today)

        # ── DSO Display ─────────────────────────────────────────────────
        dso = self.dashboard_svc.get_dso()
        dso_frame = ctk.CTkFrame(self, fg_color=theme.SURFACE_CONT,
                                 corner_radius=theme.CORNER_RADIUS)
        dso_frame.pack(fill="x", padx=24, pady=(0, 24))
        ctk.CTkLabel(dso_frame, text="DSO (Days Sales Outstanding)", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(16, 4), anchor="w")
        ctk.CTkLabel(dso_frame, text=f"{dso:.0f} jours", font=theme.FONT_KPI,
                     text_color=theme.PRIMARY).pack(padx=24, pady=(0, 16), anchor="w")

    def _get_overdue_stats(self, today):
        rows = self.conn.execute(
            """SELECT i.due_date,
                      i.amount - COALESCE(SUM(p.amount), 0) AS remaining
               FROM invoices i
               LEFT JOIN payments p ON p.invoice_id = i.id
               WHERE i.status != 'PAYEE'
               GROUP BY i.id"""
        ).fetchall()

        total_overdue = 0
        over_30 = 0
        over_90 = 0

        for row in rows:
            remaining = row["remaining"]
            if remaining <= 0:
                continue
            due = date.fromisoformat(row["due_date"])
            days = (today - due).days
            if days > 0:
                total_overdue += remaining
            if days > 30:
                over_30 += remaining
            if days > 90:
                over_90 += remaining

        return {"total_overdue": total_overdue, "over_30": over_30, "over_90": over_90}

    def _get_overdue_invoices(self, today):
        """Get all overdue invoices with remaining > 0."""
        rows = self.conn.execute(
            """SELECT i.*, c.name AS client_name, a.name AS affiliate_name,
                      COALESCE(SUM(p.amount), 0) AS total_paid
               FROM invoices i
               JOIN clients c ON i.client_id = c.id
               JOIN affiliates a ON i.affiliate_id = a.id
               LEFT JOIN payments p ON p.invoice_id = i.id
               WHERE i.status != 'PAYEE'
               GROUP BY i.id
               ORDER BY i.due_date ASC"""
        ).fetchall()

        overdue = []
        for row in rows:
            remaining = row["amount"] - row["total_paid"]
            if remaining <= 0:
                continue
            due = date.fromisoformat(row["due_date"])
            days = (today - due).days
            if days > 0:
                overdue.append({
                    "number": row["number"],
                    "client": row["client_name"],
                    "amount": row["amount"],
                    "due_date": due,
                    "days_overdue": days,
                    "status": "EN_RETARD",
                })
        return overdue

    def _load_overdue(self, today):
        all_overdue = self._get_overdue_invoices(today)
        total = len(all_overdue)
        start = self.current_page * self.PAGE_SIZE
        page_items = all_overdue[start:start + self.PAGE_SIZE]

        rows = []
        for item in page_items:
            rows.append([
                item["number"],
                item["client"],
                theme.format_fcfa(item["amount"]),
                item["due_date"].strftime("%d/%m/%Y"),
                f"{item['days_overdue']}j",
                item["status"],
            ])
        self.grid_widget.set_data(rows, total, self.current_page, self.PAGE_SIZE)

    def _on_page_change(self, page):
        self.current_page = page
        self._load_overdue(date.today())

    def _export_excel(self):
        path = filedialog.asksaveasfilename(
            title="Exporter Balance Agee",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
        )
        if not path:
            return
        try:
            self.export_svc.export_aging_excel(path)
            messagebox.showinfo("Export reussi", f"Fichier exporte:\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur d'export", str(e))

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.current_page = 0
        self._build()
