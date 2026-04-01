import customtkinter as ctk
from terminal_prime import theme

class StatusPill(ctk.CTkLabel):
    def __init__(self, parent, status):
        colors = theme.STATUS_COLORS.get(status, (theme.SURFACE_HIGHEST, theme.ON_SURFACE_VAR))
        bg, fg = colors
        super().__init__(parent, text=status.replace("_", " "),
                         font=theme.FONT_LABEL_UPPER, text_color=fg, fg_color=bg,
                         corner_radius=12, padx=10, pady=4)
