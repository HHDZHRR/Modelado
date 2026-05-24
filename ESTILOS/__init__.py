import customtkinter as ctk
from tkinter import ttk

# ── Paleta de Colores (Estilo PIA.py) ──────────────────────────────────────────
BG     = "#0D1117"
PANEL  = "#161B27"
CARD   = "#1C2333"
BORDER = "#2A3350"
GREEN  = "#00D4A0"
RED    = "#FF6B6B"
AMBER  = "#FFB347"
WHITE  = "#F0F4FF"
MUTED  = "#6B7A99"


def aplicar_tema():
    """Inicializa el modo de apariencia y el tema de color en CustomTkinter."""
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("green")


def configurar_tabla():
    """Configura el estilo visual personalizado de las tablas (Treeview) para que coincida con el tema oscuro."""
    estilo = ttk.Style()
    estilo.theme_use("clam")

    estilo.configure(
        "Treeview",
        font=("Arial", 11),
        rowheight=30,
        background=PANEL,
        fieldbackground=PANEL,
        foreground=WHITE
    )
    estilo.configure(
        "Treeview.Heading",
        font=("Arial", 10, "bold"),
        foreground=BG,
        background=GREEN,
        padding=6
    )
    estilo.map("Treeview", background=[("selected", BORDER)])
