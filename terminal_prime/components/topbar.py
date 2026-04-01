import customtkinter as ctk
from terminal_prime import theme

class Topbar(ctk.CTkFrame):
    def __init__(self, parent, title="Commercial Balance"):
        super().__init__(parent, height=64, corner_radius=0, fg_color=theme.SURFACE)
        self.pack_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text=title, font=(theme.FONT_FAMILY, 14, "bold"),
                     text_color=theme.PRIMARY).grid(row=0, column=0, padx=32, pady=16, sticky="w")

        self.search_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.search_var,
                     placeholder_text="Rechercher...", width=350, height=36,
                     corner_radius=theme.CORNER_RADIUS, fg_color=theme.SURFACE_LOWEST,
                     border_width=0, font=theme.FONT_BODY, text_color=theme.ON_SURFACE,
                     ).grid(row=0, column=1, padx=16, pady=16, sticky="w")
