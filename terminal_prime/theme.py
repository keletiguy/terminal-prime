"""Carbon Console design system constants for Terminal Prime."""

# ─── Surfaces ─────────────────────────────────────────────────────────────────
SURFACE_LOWEST = "#0e0e0e"
SURFACE = "#131313"
SURFACE_LOW = "#1c1b1b"
SURFACE_CONT = "#20201f"
SURFACE_HIGH = "#2a2a2a"
SURFACE_BRIGHT = "#393939"
SURFACE_HIGHEST = "#353535"

# ─── Colors ───────────────────────────────────────────────────────────────────
PRIMARY = "#a5c8ff"
PRIMARY_CONT = "#1f538d"
SECONDARY = "#b7c7e4"
SECONDARY_CONT = "#3a4a61"
TERTIARY = "#fdbb2e"
TERTIARY_CONT = "#6d4c00"
ERROR = "#ffb4ab"
ERROR_CONT = "#93000a"

# ─── Text ─────────────────────────────────────────────────────────────────────
ON_SURFACE = "#e5e2e1"
ON_SURFACE_VAR = "#c2c6d1"
ON_PRIMARY = "#00315e"
ON_ERROR = "#690005"
OUTLINE = "#8c919b"
OUTLINE_VAR = "#424750"

# ─── Design constants ────────────────────────────────────────────────────────
CORNER_RADIUS = 10
FONT_FAMILY = "Inter"

# Font tuples: (family, size, weight)
HEADING = (FONT_FAMILY, 24, "bold")
TITLE = (FONT_FAMILY, 18, "bold")
BODY = (FONT_FAMILY, 14)
BODY_BOLD = (FONT_FAMILY, 14, "bold")
LABEL = (FONT_FAMILY, 12)
LABEL_UPPER = (FONT_FAMILY, 11, "bold")
SMALL = (FONT_FAMILY, 10)
KPI = (FONT_FAMILY, 32, "bold")

# Status colors
STATUS_COLORS = {
    "EN_ATTENTE": SECONDARY,
    "PAYEE": "#66bb6a",
    "PARTIELLE": TERTIARY,
    "EN_RETARD": ERROR,
}

# ─── Window dimensions ───────────────────────────────────────────────────────
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 850
SIDEBAR_WIDTH = 250


# ─── Helpers ──────────────────────────────────────────────────────────────────
def format_fcfa(amount: int) -> str:
    """Format an integer amount as FCFA currency string."""
    return f"{amount:,.0f} FCFA".replace(",", " ")
