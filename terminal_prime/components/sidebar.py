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
                         fg_color=theme.SURFACE_LOW)
        self.on_navigate = on_navigate
        self.active_key = "dashboard"
        self.buttons = {}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)

        # Logo section
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
                fg_color="transparent", text_color=theme.ON_SURFACE_VAR,
                hover_color=theme.SURFACE_HIGH,
                command=lambda k=key: self._on_click(k),
            )
            btn.pack(fill="x", pady=2)
            self.buttons[key] = btn

        # Profile section at bottom
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

    def _on_click(self, key):
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
