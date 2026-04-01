import customtkinter as ctk
from terminal_prime import theme


class KpiCard(ctk.CTkFrame):
    def __init__(self, parent, label, value, badge="", badge_color=None, value_color=None):
        super().__init__(parent, fg_color=theme.SURFACE_CONT, corner_radius=theme.CORNER_RADIUS)
        self._label_widget = ctk.CTkLabel(self, text=label.upper(), font=theme.FONT_LABEL_UPPER,
                     text_color=theme.ON_SURFACE_VAR)
        self._label_widget.pack(padx=24, pady=(20, 8), anchor="w")

        self._value_widget = ctk.CTkLabel(self, text=value, font=theme.FONT_KPI,
                     text_color=value_color or theme.ON_SURFACE)
        self._value_widget.pack(padx=24, anchor="w")

        self._badge_widget = ctk.CTkLabel(self, text=badge or "", font=theme.FONT_SMALL,
                     text_color=badge_color or theme.PRIMARY,
                     fg_color=theme.SURFACE_HIGH if badge else "transparent",
                     corner_radius=12, padx=8, pady=2)
        self._badge_widget.pack(padx=24, pady=(8, 20), anchor="w")

    def update_values(self, value, badge="", value_color=None, badge_color=None):
        """Update displayed values without recreating widgets."""
        self._value_widget.configure(text=value, text_color=value_color or theme.ON_SURFACE)
        if badge:
            self._badge_widget.configure(text=badge, fg_color=theme.SURFACE_HIGH,
                                          text_color=badge_color or theme.PRIMARY)
        else:
            self._badge_widget.configure(text="", fg_color="transparent")
