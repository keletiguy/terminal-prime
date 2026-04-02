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
        self._dirty = set()
        self._active_key = None
        self._view_factories = {
            "dashboard": lambda: DashboardView(self.content, self.conn),
            "invoices": lambda: InvoicesView(self.content, self.conn,
                                              on_data_changed=self._mark_all_dirty,
                                              on_open_collection=self._open_collection),
            "collections": lambda: CollectionsView(self.content, self.conn, on_data_changed=self._mark_all_dirty),
            "analysis": lambda: ClientAnalysisView(self.content, self.conn),
            "reports": lambda: ReportsView(self.content, self.conn),
        }
        self._navigate("dashboard")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_or_create_view(self, key):
        if key not in self.views:
            self.views[key] = self._view_factories[key]()
            self.views[key].grid(row=0, column=0, sticky="nsew")
        return self.views[key]

    def _navigate(self, key):
        if key == self._active_key:
            return
        for view in self.views.values():
            view.grid_remove()
        view = self._get_or_create_view(key)
        view.grid()
        self._active_key = key
        if key in self._dirty:
            self._dirty.discard(key)
            if hasattr(view, 'refresh'):
                self.after(50, view.refresh)

    def _open_collection(self, invoice):
        """Navigate to collections with an invoice pre-selected."""
        self.sidebar.active_key = "collections"
        self.sidebar._update_active()
        # Force navigate even if already on collections
        self._active_key = None
        self._navigate("collections")
        # Pre-select the invoice after view is ready
        self.after(100, lambda: self.views["collections"].select_invoice(invoice))

    def _mark_all_dirty(self):
        """Mark all views except the active one as needing refresh."""
        for key in self.views:
            if key != self._active_key:
                self._dirty.add(key)
        # Refresh the active view immediately
        if self._active_key and hasattr(self.views[self._active_key], 'refresh'):
            self.views[self._active_key].refresh()

    def _on_close(self):
        close_connection()
        self.destroy()
