"""Client analysis view with aging breakdown and timeline chart."""
import sqlite3
from datetime import date
from typing import Optional

import customtkinter as ctk

from terminal_prime import theme
from terminal_prime.components.kpi_card import KpiCard
from terminal_prime.components.bar_chart import BarChart
from terminal_prime.database.client_repo import ClientRepo
from terminal_prime.services.aging_service import AgingService
from terminal_prime.services.dashboard_service import DashboardService


class ClientAnalysisView(ctk.CTkScrollableFrame):
    def __init__(self, parent, conn: sqlite3.Connection):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.client_repo = ClientRepo(conn)
        self.aging_svc = AgingService(conn)
        self.dashboard_svc = DashboardService(conn)
        self._clients = []
        self._client_map = {}
        self._detail_frame = None
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Analyse Client", font=theme.FONT_HEADING,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(24, 16), anchor="w")

        # ── Client Selector ─────────────────────────────────────────────
        selector = ctk.CTkFrame(self, fg_color="transparent")
        selector.pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkLabel(selector, text="CLIENT", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(side="left", padx=(0, 12))

        self._clients = self.client_repo.get_all()
        self._client_map = {c.name: c.id for c in self._clients}
        client_names = [c.name for c in self._clients]

        self.client_var = ctk.StringVar()
        self.client_dd = ctk.CTkOptionMenu(
            selector, values=client_names or ["--"], variable=self.client_var,
            fg_color=theme.SURFACE_LOWEST, button_color=theme.SURFACE_HIGH,
            font=theme.FONT_BODY, width=300,
            command=self._on_client_selected)
        self.client_dd.pack(side="left")

        # Detail area
        self._detail_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._detail_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        if client_names:
            self.client_var.set(client_names[0])
            self._on_client_selected(client_names[0])

    def _on_client_selected(self, name):
        client_id = self._client_map.get(name)
        if client_id is None:
            return

        # Clear detail area
        for widget in self._detail_frame.winfo_children():
            widget.destroy()

        # Client name header
        ctk.CTkLabel(self._detail_frame, text=name, font=theme.FONT_TITLE,
                     text_color=theme.PRIMARY).pack(pady=(0, 16), anchor="w")

        # ── Aging Breakdown (5 KPI-style boxes) ─────────────────────────
        buckets = self.aging_svc.get_client_aging(client_id)
        aging_row = ctk.CTkFrame(self._detail_frame, fg_color="transparent")
        aging_row.pack(fill="x", pady=(0, 16))
        aging_row.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        labels = ["Courant", "0-30j", "31-60j", "61-90j", "90+j"]
        keys = ["current", "0-30", "31-60", "61-90", "90+"]
        colors = [theme.PRIMARY, theme.PRIMARY, theme.TERTIARY,
                  theme.TERTIARY_CONT, theme.ERROR]

        for i, (lbl, key, color) in enumerate(zip(labels, keys, colors)):
            box = ctk.CTkFrame(aging_row, fg_color=theme.SURFACE_CONT,
                               corner_radius=theme.CORNER_RADIUS)
            box.grid(row=0, column=i, padx=4, sticky="nsew")
            ctk.CTkLabel(box, text=lbl.upper(), font=theme.FONT_LABEL_UPPER,
                         text_color=theme.ON_SURFACE_VAR).pack(padx=16, pady=(12, 4), anchor="w")
            ctk.CTkLabel(box, text=theme.format_fcfa(buckets[key]),
                         font=theme.FONT_BODY_BOLD, text_color=color
                         ).pack(padx=16, pady=(0, 12), anchor="w")

        # ── Total Balance KPI ────────────────────────────────────────────
        total_balance = sum(buckets.values())
        balance_color = theme.ERROR if total_balance > 0 else theme.ON_SURFACE
        KpiCard(self._detail_frame, label="Balance Totale",
                value=theme.format_fcfa(total_balance),
                value_color=balance_color).pack(fill="x", pady=(0, 16))

        # ── Timeline Bar Chart (6 months) ────────────────────────────────
        self._timeline_chart = BarChart(self._detail_frame,
                                        title="Historique 6 Mois",
                                        subtitle="Factures vs Paiements")
        self._timeline_chart.pack(fill="x", pady=(0, 16))

        # Delay chart rendering
        self.after(200, lambda: self._load_timeline(client_id))

    def _month_subtract(self, ref_date, months):
        month = ref_date.month - months
        year = ref_date.year
        while month <= 0:
            month += 12
            year -= 1
        return date(year, month, 1)

    def _load_timeline(self, client_id):
        today = date.today()
        bars = []

        for i in range(5, -1, -1):
            month_start = self._month_subtract(today, i)
            if i > 0:
                month_end = self._month_subtract(today, i - 1) - __import__('datetime').timedelta(days=1)
            else:
                month_end = today

            # Invoices in this month
            row = self.conn.execute(
                "SELECT COALESCE(SUM(amount), 0) AS total FROM invoices "
                "WHERE client_id = ? AND date >= ? AND date <= ?",
                (client_id, month_start.isoformat(), month_end.isoformat()),
            ).fetchone()
            inv_total = row["total"]

            # Payments in this month
            row = self.conn.execute(
                "SELECT COALESCE(SUM(amount), 0) AS total FROM payments "
                "WHERE client_id = ? AND date >= ? AND date <= ?",
                (client_id, month_start.isoformat(), month_end.isoformat()),
            ).fetchone()
            pay_total = row["total"]

            month_label = month_start.strftime("%b")
            # Show as paired bars: use invoice amount with primary color
            # We combine into a single bar showing net (invoices - payments)
            bars.append((month_label, max(inv_total, 1), theme.PRIMARY))

        self._timeline_chart.set_data(bars)

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build()
