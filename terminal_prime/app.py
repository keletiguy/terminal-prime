import os
import shutil
from datetime import datetime
import customtkinter as ctk
from terminal_prime import theme
from terminal_prime.database.connection import get_connection, close_connection, get_db_path
from terminal_prime.database.schema import create_tables
from terminal_prime.components.sidebar import Sidebar
from terminal_prime.components.topbar import Topbar
from terminal_prime.views.dashboard_view import DashboardView
from terminal_prime.views.invoices_view import InvoicesView
from terminal_prime.views.collections_view import CollectionsView
from terminal_prime.views.client_analysis_view import ClientAnalysisView
from terminal_prime.views.reports_view import ReportsView

BACKUP_DIR = "backups"
BACKUP_INTERVAL_MS = 30 * 60 * 1000  # 30 minutes
MAX_BACKUPS = 10


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Terminal Prime - Balance Commerciale")
        self.geometry(f"{theme.WINDOW_WIDTH}x{theme.WINDOW_HEIGHT}")
        self.minsize(theme.WINDOW_MIN_WIDTH, theme.WINDOW_MIN_HEIGHT)

        self.conn = get_connection()
        create_tables(self.conn)

        self._active_key = None
        self._dirty = set()

        self._build_ui()

        # Listen for theme changes
        theme.on_theme_change(self._on_theme_change)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._schedule_backup()

    def _build_ui(self):
        """Build or rebuild the entire UI."""
        # Destroy existing children
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(fg_color=theme.SURFACE)

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
        self._view_factories = {
            "dashboard": lambda: DashboardView(self.content, self.conn),
            "invoices": lambda: InvoicesView(self.content, self.conn,
                                              on_data_changed=self._mark_all_dirty,
                                              on_open_collection=self._open_collection),
            "collections": lambda: CollectionsView(self.content, self.conn, on_data_changed=self._mark_all_dirty),
            "analysis": lambda: ClientAnalysisView(self.content, self.conn),
            "reports": lambda: ReportsView(self.content, self.conn),
        }

        saved_key = self._active_key or "dashboard"
        self._active_key = None
        self._navigate(saved_key)

    def _on_theme_change(self, theme_name):
        """Rebuild UI when theme changes."""
        mode = "light" if theme_name == "light" else "dark"
        ctk.set_appearance_mode(mode)
        self._build_ui()

    def _get_or_create_view(self, key):
        if key not in self.views:
            self.views[key] = self._view_factories[key]()
            self.views[key].grid(row=0, column=0, sticky="nsew")
        return self.views[key]

    def _navigate(self, key):
        if key == self._active_key:
            if key == "dashboard" and key in self.views:
                self.views[key].refresh()
            return
        for view in self.views.values():
            view.grid_remove()
        view = self._get_or_create_view(key)
        view.grid()
        self._active_key = key
        self._dirty.discard(key)
        if hasattr(view, 'refresh'):
            self.after(50, view.refresh)

    def _open_collection(self, invoice):
        self.sidebar.active_key = "collections"
        self.sidebar._update_active()
        self._active_key = None
        self._navigate("collections")
        self.after(100, lambda: self.views["collections"].select_invoice(invoice))

    def _mark_all_dirty(self):
        for key in self.views:
            if key != self._active_key:
                self._dirty.add(key)
        if self._active_key and hasattr(self.views[self._active_key], 'refresh'):
            self.views[self._active_key].refresh()

    def _schedule_backup(self):
        self._do_backup()
        self.after(BACKUP_INTERVAL_MS, self._schedule_backup)

    def _do_backup(self):
        db_path = get_db_path()
        if not db_path or not os.path.exists(db_path):
            return
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"terminal_prime_backup_{timestamp}.db")
        try:
            shutil.copy2(db_path, backup_path)
            self._cleanup_old_backups()
        except Exception:
            pass

    def _cleanup_old_backups(self):
        if not os.path.exists(BACKUP_DIR):
            return
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")], reverse=True)
        for old in backups[MAX_BACKUPS:]:
            try:
                os.remove(os.path.join(BACKUP_DIR, old))
            except Exception:
                pass

    def _on_close(self):
        self._do_backup()
        close_connection()
        self.destroy()
