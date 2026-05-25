# ==============================================================================
# VERIFICACIÓN E INSTALACIÓN AUTOMÁTICA DE LIBRERÍAS (Para el Profesor)
# ==============================================================================
import importlib
import subprocess
import sys

for pkg, spec in [
    ("customtkinter", "customtkinter==5.2.2"),
    ("matplotlib", "matplotlib==3.10.9"),
    ("numpy", "numpy==2.4.6"),
    ("PIL", "pillow==12.2.0"),
    ("scipy", "scipy==1.17.1")
]:
    try:
        importlib.import_module(pkg)
    except ImportError:
        print(f"Instalando libreria faltante: {spec}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", spec])
        except Exception as e:
            print(f"Error al instalar {spec}: {e}")
# ==============================================================================

import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
from scipy.optimize import brentq

# ── Paleta de Colores ─────────────────────────────────────────────────────────
BG     = "#0D1117"
PANEL  = "#161B27"
CARD   = "#1C2333"
BORDER = "#2A3350"
GREEN  = "#00D4A0"
RED    = "#FF6B6B"
AMBER  = "#FFB347"
WHITE  = "#F0F4FF"
MUTED  = "#6B7A99"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

# ── Lógica Matemática ─────────────────────────────────────────────────────────
def calcular_tir(inversion, flujos):
    def vpn(r):
        return -inversion + sum(f/(1+r)**(t+1) for t,f in enumerate(flujos))
    try:
        return brentq(vpn, -0.999, 50.0, xtol=1e-10, maxiter=200) * 100
    except (ValueError, RuntimeError):
        return None

def simular(inv_mu, inv_sig, flu_mu, flu_sig, n_sim):
    rng = np.random.default_rng()
    inv = rng.normal(inv_mu, inv_sig, n_sim)
    flu = rng.normal(flu_mu, flu_sig, (n_sim, 5))
    out = []
    for i in range(n_sim):
        t = calcular_tir(inv[i], flu[i])
        if t is not None and -90 < t < 5000:
            out.append(t)
    return np.array(out)

def estadisticas(tirs, trema):
    if len(tirs) == 0:
        return None
    return dict(n=len(tirs), media=np.mean(tirs), std=np.std(tirs),
                p10=np.percentile(tirs, 10), p90=np.percentile(tirs, 90),
                prob=np.mean(tirs > trema) * 100)

# ── Interfaz Gráfica (UI) ─────────────────────────────────────────────────────
class AppMonteCarlo(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulador Monte Carlo - Evaluación de Proyectos")
        self.geometry("1100x650")
        self.state('zoomed')
        self.configure(fg_color=BG)
        self.minsize(900, 600)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_sidebar()
        self.crear_panel_principal()
        self.ejecutar_simulacion()

    def crear_sidebar(self):
        self.sidebar = ctk.CTkScrollableFrame(self, width=280, fg_color=PANEL, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="Parámetros",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=WHITE).pack(pady=(20, 20), padx=20, anchor="w")

        self.vars = {
            "inv_mu":  {"label": "Inversión media",    "min": 50000,  "max": 200000, "val": 100000, "fmt": "${:,.0f}"},
            "inv_sig": {"label": "Inv. Desv. Std",     "min": 1000,   "max": 30000,  "val": 5000,   "fmt": "${:,.0f}"},
            "flu_mu":  {"label": "Flujo neto medio",   "min": 5000,   "max": 80000,  "val": 30000,  "fmt": "${:,.0f}"},
            "flu_sig": {"label": "Flujo Desv. Std",    "min": 500,    "max": 15000,  "val": 3000,   "fmt": "${:,.0f}"},
            "trema":   {"label": "TREMA (%)",           "min": 5,      "max": 60,     "val": 30,     "fmt": "{:.0f}%"},
            "n_sim":   {"label": "Num. Simulaciones",  "min": 1000,   "max": 20000,  "val": 10000,  "fmt": "{:,.0f}"},
        }
        self.sliders = {}
        self.labels  = {}

        for key, cfg in self.vars.items():
            lbl = ctk.CTkLabel(self.sidebar,
                               text=f"{cfg['label']}: {cfg['fmt'].format(cfg['val'])}",
                               text_color=MUTED,
                               font=ctk.CTkFont(size=13, weight="bold"))
            lbl.pack(padx=20, pady=(10, 0), anchor="w")
            self.labels[key] = lbl

            sl = ctk.CTkSlider(self.sidebar, from_=cfg["min"], to=cfg["max"],
                               number_of_steps=200,
                               progress_color=GREEN, button_color=WHITE,
                               button_hover_color=GREEN)
            sl.set(cfg["val"])
            sl.configure(command=lambda v, k=key, f=cfg["fmt"], l=cfg["label"]:
                         self.actualizar_label(v, k, f, l))
            sl.pack(padx=20, pady=(5, 10), fill="x")
            self.sliders[key] = sl

        self.btn_ejecutar = ctk.CTkButton(
            self.sidebar, text="EJECUTAR SIMULACIÓN",
            fg_color=GREEN, text_color=BG, hover_color="#00B889",
            font=ctk.CTkFont(size=14, weight="bold"), height=45,
            command=self.ejecutar_simulacion)
        self.btn_ejecutar.pack(padx=20, pady=30, fill="x")

    def actualizar_label(self, val, key, fmt, label_text):
        self.labels[key].configure(text=f"{label_text}: {fmt.format(val)}")

    def crear_panel_principal(self):
        self.main_frame = ctk.CTkFrame(self, fg_color=BG)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.cards = {}
        metricas = ["TIR Media", "Desv. Std", "P(TIR > TREMA)", "Percentil 10%"]

        for i, m in enumerate(metricas):
            frame = ctk.CTkFrame(self.main_frame, fg_color=CARD, corner_radius=10, height=80)
            frame.grid(row=0, column=i, padx=5, pady=(0, 20), sticky="ew")
            frame.grid_propagate(False)

            ctk.CTkLabel(frame, text=m, text_color=MUTED,
                         font=ctk.CTkFont(size=12)).place(relx=0.5, rely=0.3, anchor="center")
            val_lbl = ctk.CTkLabel(frame, text="--", text_color=WHITE,
                                   font=ctk.CTkFont(size=22, weight="bold"))
            val_lbl.place(relx=0.5, rely=0.7, anchor="center")
            self.cards[m] = val_lbl

        self.fig, self.ax = plt.subplots(figsize=(8, 5), facecolor=PANEL)
        self.ax.set_facecolor(PANEL)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=(0, 20))

        self.veredicto_frame = ctk.CTkFrame(self.main_frame, fg_color=CARD, height=50, corner_radius=10)
        self.veredicto_frame.grid(row=2, column=0, columnspan=4, sticky="ew")
        self.veredicto_frame.grid_propagate(False)
        self.veredicto_lbl = ctk.CTkLabel(self.veredicto_frame, text="Esperando ejecución...",
                                          font=ctk.CTkFont(size=16, weight="bold"))
        self.veredicto_lbl.place(relx=0.5, rely=0.5, anchor="center")

    def ejecutar_simulacion(self):
        self.btn_ejecutar.configure(state="disabled", text="CALCULANDO...")
        self.update()

        p = {k: float(v.get()) for k, v in self.sliders.items()}
        n = int(p["n_sim"])

        # FIX PRINCIPAL: tirs se calcula aquí y se pasa a actualizar_ui
        tirs = simular(p["inv_mu"], p["inv_sig"], p["flu_mu"], p["flu_sig"], n)
        est  = estadisticas(tirs, p["trema"])

        if est:
            self.actualizar_ui(tirs, est, p["trema"])   # ← tirs incluido

        self.btn_ejecutar.configure(state="normal", text="EJECUTAR SIMULACIÓN")

    # FIX: actualizar_ui ahora recibe tirs como primer argumento
    def actualizar_ui(self, tirs, est, trema):
        ok = est["prob"] >= 90

        self.cards["TIR Media"].configure(text=f"{est['media']:.2f}%")
        self.cards["Desv. Std"].configure(text=f"{est['std']:.2f}%")
        self.cards["P(TIR > TREMA)"].configure(
            text=f"{est['prob']:.2f}%",
            text_color=GREEN if ok else RED)
        self.cards["Percentil 10%"].configure(text=f"{est['p10']:.2f}%")

        if ok:
            msg = f"ACEPTAR PROYECTO: Probabilidad del {est['prob']:.1f}% cumple con el criterio (>= 90%)"
            self.veredicto_frame.configure(fg_color="#0A3D2E", border_color=GREEN, border_width=2)
            self.veredicto_lbl.configure(text=msg, text_color=GREEN)
        else:
            msg = f"RECHAZAR PROYECTO: Probabilidad del {est['prob']:.1f}% no cumple con el criterio de riesgo"
            self.veredicto_frame.configure(fg_color="#3D0A0A", border_color=RED, border_width=2)
            self.veredicto_lbl.configure(text=msg, text_color=RED)

        # ── Gráfica ──────────────────────────────────────────────────────────
        self.ax.clear()
        self.ax.set_facecolor(PANEL)
        for spine in self.ax.spines.values():
            spine.set_color(BORDER)
        self.ax.tick_params(colors=MUTED)

        counts, bins, patches = self.ax.hist(tirs, bins=50, edgecolor=PANEL, linewidth=0.5)
        bw = bins[1] - bins[0]

        for patch, le in zip(patches, bins[:-1]):
            c = le + bw / 2
            patch.set_facecolor(GREEN if c > trema else RED)
            patch.set_alpha(0.85)

        self.ax.axvspan(bins[0],  trema,    alpha=0.1, color=RED)
        self.ax.axvspan(trema,    bins[-1], alpha=0.1, color=GREEN)

        # FIX LEYENDA: guardar referencias directas en lugar de ax.lines[0/1]
        linea_trema = self.ax.axvline(trema,          color=AMBER, lw=2,   ls="--")
        linea_media = self.ax.axvline(est["media"],   color=WHITE, lw=1.5, ls=":")

        self.ax.set_title("Distribución de la Tasa Interna de Retorno (TIR)",
                          color=WHITE, pad=15)
        self.ax.set_xlabel("TIR (%)", color=MUTED, fontsize=10)

        g_patch = mpatches.Patch(color=GREEN, label="TIR > TREMA")
        r_patch = mpatches.Patch(color=RED,   label="TIR <= TREMA")
        linea_trema.set_label(f"TREMA ({trema:.0f}%)")
        linea_media.set_label(f"Media ({est['media']:.1f}%)")

        self.ax.legend(handles=[g_patch, r_patch, linea_trema, linea_media],
                       facecolor=CARD, edgecolor=BORDER, labelcolor=WHITE,
                       loc="upper right")

        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = AppMonteCarlo()
    app.mainloop()