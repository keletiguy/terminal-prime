"""Dashboard view with KPIs, aging chart, performance panel, and top debtors."""
import sqlite3
import customtkinter as ctk
from terminal_prime import theme
from terminal_prime.components.kpi_card import KpiCard
from terminal_prime.components.bar_chart import BarChart
from terminal_prime.components.progress_bar import GradientProgressBar
from terminal_prime.components.data_grid import DataGrid
from terminal_prime.services.dashboard_service import DashboardService
from terminal_prime.services.aging_service import AgingService


class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, parent, conn: sqlite3.Connection):
        super().__init__(parent, fg_color=theme.SURFACE, corner_radius=0)
        self.conn = conn
        self.dashboard_svc = DashboardService(conn)
        self.aging_svc = AgingService(conn)
        self._built = False
        self._build()

    def _build(self):
        # KPI Row
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.pack(fill="x", padx=24, pady=(24, 16))
        kpi_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="kpi")

        self.kpi_emis = KpiCard(kpi_row, label="Total Emis", value="0 FCFA")
        self.kpi_emis.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        self.kpi_recouvre = KpiCard(kpi_row, label="Total Recouvre", value="0 FCFA")
        self.kpi_recouvre.grid(row=0, column=1, padx=8, sticky="nsew")

        self.kpi_solde = KpiCard(kpi_row, label="Solde Global", value="0 FCFA")
        self.kpi_solde.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        # Middle Row
        mid_row = ctk.CTkFrame(self, fg_color="transparent")
        mid_row.pack(fill="x", padx=24, pady=(0, 16))
        mid_row.grid_columnconfigure(0, weight=2)
        mid_row.grid_columnconfigure(1, weight=1)

        self.aging_chart = BarChart(mid_row, title="Balance Agee",
                                    subtitle="Repartition par tranche d'echeance")
        self.aging_chart.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        # Performance panel
        perf_panel = ctk.CTkFrame(mid_row, fg_color=theme.SURFACE_CONT,
                                  corner_radius=theme.CORNER_RADIUS)
        perf_panel.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(perf_panel, text="Performance", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(20, 16), anchor="w")

        self.progress = GradientProgressBar(perf_panel, label="Taux de Recouvrement",
                                             value=0, max_label="0%")
        self.progress.pack(fill="x", padx=24, pady=(0, 16))

        dso_box = ctk.CTkFrame(perf_panel, fg_color=theme.SURFACE_LOW,
                               corner_radius=theme.CORNER_RADIUS)
        dso_box.pack(fill="x", padx=24, pady=(0, 8))
        ctk.CTkLabel(dso_box, text="DSO", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=16, pady=(12, 4), anchor="w")
        self.dso_label = ctk.CTkLabel(dso_box, text="0 jours", font=theme.FONT_BODY_BOLD,
                     text_color=theme.ON_SURFACE)
        self.dso_label.pack(padx=16, pady=(0, 12), anchor="w")

        cei_box = ctk.CTkFrame(perf_panel, fg_color=theme.SURFACE_LOW,
                               corner_radius=theme.CORNER_RADIUS)
        cei_box.pack(fill="x", padx=24, pady=(0, 20))
        ctk.CTkLabel(cei_box, text="CEI", font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR).pack(padx=16, pady=(12, 4), anchor="w")
        self.cei_label = ctk.CTkLabel(cei_box, text="0%", font=theme.FONT_BODY_BOLD,
                     text_color=theme.ON_SURFACE)
        self.cei_label.pack(padx=16, pady=(0, 12), anchor="w")

        # Top 5 Debtors
        ctk.CTkLabel(self, text="Top 5 Debiteurs", font=theme.FONT_TITLE,
                     text_color=theme.ON_SURFACE).pack(padx=24, pady=(0, 8), anchor="w")

        self.debtors_grid = DataGrid(
            self, columns=[("Client", 250), ("Total Du", 150), ("Statut", 120)],
            status_columns={2})
        self.debtors_grid.pack(fill="x", padx=24, pady=(0, 24))

        self._built = True
        self._update_data()

    def _update_data(self):
        """Update all data without recreating widgets."""
        kpis = self.dashboard_svc.get_kpis()
        self.kpi_emis.update_values(theme.format_fcfa(kpis["total_issued"]))
        self.kpi_recouvre.update_values(theme.format_fcfa(kpis["total_collected"]))
        solde_color = theme.ERROR if kpis["outstanding"] > 0 else theme.ON_SURFACE
        self.kpi_solde.update_values(theme.format_fcfa(kpis["outstanding"]), value_color=solde_color)

        # Aging chart
        buckets = self.aging_svc.get_aging_buckets()
        colors = [theme.PRIMARY, theme.PRIMARY, theme.TERTIARY, theme.TERTIARY_CONT, theme.ERROR]
        labels = ["Courant", "0-30j", "31-60j", "61-90j", "90+j"]
        keys = ["current", "0-30", "31-60", "61-90", "90+"]
        self.aging_chart.set_data([(labels[i], buckets[keys[i]], colors[i]) for i in range(5)])

        # Performance
        rate = self.dashboard_svc.get_collection_rate()
        self.progress.set_value(rate)
        dso = self.dashboard_svc.get_dso()
        self.dso_label.configure(text=f"{dso:.0f} jours")
        cei = self.dashboard_svc.get_cei()
        self.cei_label.configure(text=f"{cei:.1f}%")

        # Top debtors
        debtors = self.dashboard_svc.get_top_debtors(5)
        rows = []
        for d in debtors:
            rows.append([d["name"], theme.format_fcfa(d["total_due"]), "EN_RETARD"])
        self.debtors_grid.set_data(rows, len(rows), 0, max(len(rows), 1))

    def refresh(self):
        """Refresh data only, no widget rebuild."""
        if self._built:
            self._update_data()
