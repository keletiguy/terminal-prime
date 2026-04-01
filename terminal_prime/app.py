import customtkinter as ctk
from terminal_prime import theme
from terminal_prime.database.connection import get_connection, close_connection
from terminal_prime.database.schema import create_tables
from terminal_prime.components.sidebar import Sidebar
from terminal_prime.components.topbar import Topbar
from terminal_prime.views.dashboard_view import DashboardView
from terminal_prime.views.invoices_view import InvoicesView
from terminal_prime.views.collections_view import CollectionsView
from terminal_prime.views.client_analysis_view import ClientAnalysisView
from terminal_prime.views.reports_view import ReportsView


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Terminal Prime - Balance Commerciale")
        self.geometry(f"{theme.WINDOW_WIDTH}x{theme.WINDOW_HEIGHT}")
        self.minsize(theme.WINDOW_MIN_WIDTH, theme.WINDOW_MIN_HEIGHT)
        self.configure(fg_color=theme.SURFACE)

        self.conn = get_connection()
        create_tables(self.conn)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_navigate=self._navigate)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        main = ctk.CTkFrame(self, fg_color=theme.SURFACE, corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self.topbar = Topbar(main)
        self.topbar.grid(row=0, column=0, sticky="new")

        self.content = ctk.CTkFrame(main, fg_color=theme.SURFACE, corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.views = {}
        self._create_views()
        self._navigate("dashboard")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_views(self):
        self.views["dashboard"] = DashboardView(self.content, self.conn)
        self.views["invoices"] = InvoicesView(self.content, self.conn, on_data_changed=self._refresh_all)
        self.views["collections"] = CollectionsView(self.content, self.conn, on_data_changed=self._refresh_all)
        self.views["analysis"] = ClientAnalysisView(self.content, self.conn)
        self.views["reports"] = ReportsView(self.content, self.conn)
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def _navigate(self, key):
        for view in self.views.values():
            view.grid_remove()
        self.views[key].grid()
        if hasattr(self.views[key], 'refresh'):
            self.views[key].refresh()

    def _refresh_all(self):
        for view in self.views.values():
            if hasattr(view, 'refresh'):
                view.refresh()

    def _on_close(self):
        close_connection()
        self.destroy()
