import customtkinter as ctk
import ESTILOS
import math
from tkinter import messagebox

ESTILOS.aplicar_tema()


def analizar_modulo(m):
    """
    Determina la naturaleza del módulo m y calcula su Periodo Esperado (P.E.)
    retornando (tipo, formula, periodo).
    """
    if m <= 0:
        return "Inválido", "Módulo debe ser mayor a cero", 0

    # Detección de Binario (Potencia de 2)
    if (m & (m - 1) == 0) and m > 0:
        formula_str = f"p.e. = m / 4\n= {m} / 4\n= {m // 4}"
        return "Binario (Potencia de 2)", formula_str, m // 4

    # Detección de Decimal (Potencia de 10)
    try:
        log10 = math.log10(m)
        if log10.is_integer():
            d = int(log10)
            if d >= 5:
                pe = 5 * (10 ** (d - 2))
                formula_str = f"p.e. = 5 * 10^(d-2)\n= 5 * 10^({d}-2)\n= 5 * 10^{d-2}\n= {pe}"
            else:
                # Cálculo de lambda para d < 5
                l5 = (5 ** (d - 1)) * 4
                l2 = 2 if d == 1 else 2 ** (d - 2)
                pe = math.lcm(l5, l2)  # MCM
                formula_str = (
                    f"p.e. = mcm[ 5^(d-1) * 4 , 2^(d-2) ]\n"
                    f"= mcm[ 5^({d}-1) * 4 , 2^({d}-2) ]\n"
                    f"= mcm[ {l5} , {l2} ]\n"
                    f"= {pe}"
                )
            return "Decimal (Potencia de 10)", formula_str, pe
    except Exception:
        pass

    return "Especial", "No aplica fórmula clásica de potencia de 2 o 10", m


class PeriodosEsperadosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Periodos Esperados | Modelado y Simulación")
        self.geometry("700x520")
        self.configure(fg_color=ESTILOS.BG)
        self.minsize(600, 450)

        # Rejilla
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_interfaz()

    def crear_interfaz(self):
        # ── PANEL IZQUIERDO (Sidebar) ──
        panel_entrada = ctk.CTkFrame(self, width=240, fg_color=ESTILOS.PANEL, corner_radius=0)
        panel_entrada.grid(row=0, column=0, sticky="nsew")
        panel_entrada.grid_propagate(False)

        ctk.CTkLabel(
            panel_entrada,
            text="Parámetros",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ESTILOS.WHITE
        ).pack(pady=(20, 20), padx=20, anchor="w")

        ctk.CTkLabel(
            panel_entrada,
            text="Módulo (m):",
            anchor="w",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=20, pady=(5, 2))

        self.ent_m = ctk.CTkEntry(
            panel_entrada,
            height=34,
            fg_color=ESTILOS.CARD,
            border_color=ESTILOS.BORDER,
            text_color=ESTILOS.WHITE
        )
        self.ent_m.pack(fill="x", padx=20, pady=(0, 15))
        self.ent_m.insert(0, "32")

        # Botones
        ctk.CTkButton(
            panel_entrada,
            text="ANALIZAR MÓDULO",
            height=40,
            fg_color=ESTILOS.GREEN,
            text_color=ESTILOS.BG,
            hover_color="#00B889",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.analizar
        ).pack(fill="x", padx=20, pady=(15, 8))

        ctk.CTkButton(
            panel_entrada,
            text="LIMPIAR",
            height=34,
            fg_color=ESTILOS.CARD,
            text_color=ESTILOS.WHITE,
            border_color=ESTILOS.BORDER,
            border_width=1,
            hover_color=ESTILOS.PANEL,
            command=self.limpiar
        ).pack(fill="x", padx=20, pady=(0, 20))

        # ── PANEL DERECHO (Resultados) ──
        panel_resultados = ctk.CTkFrame(self, fg_color=ESTILOS.BG)
        panel_resultados.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        panel_resultados.grid_columnconfigure(0, weight=1)

        # Encabezado
        ctk.CTkLabel(
            panel_resultados,
            text="ANÁLISIS DE PERIODOS ESPERADOS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ESTILOS.WHITE
        ).pack(anchor="w", pady=(10, 2))

        ctk.CTkLabel(
            panel_resultados,
            text="Determina el Periodo Esperado máximo según la base del módulo (m)",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=(0, 15))

        # Tarjetas de resultado
        self.tar_tipo = self.crear_tarjeta(panel_resultados, "Tipo de Módulo Detectado")
        self.tar_pe = self.crear_tarjeta(panel_resultados, "Periodo Esperado (P.E.)")

        # Tarjeta para Fórmula (Caja de Texto)
        ctk.CTkLabel(
            panel_resultados,
            text="Fórmula y Desarrollo:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ESTILOS.MUTED
        ).pack(fill="x", pady=(10, 2), anchor="w")

        self.txt_formula = ctk.CTkTextbox(
            panel_resultados,
            height=120,
            fg_color=ESTILOS.CARD,
            border_color=ESTILOS.BORDER,
            border_width=1,
            text_color=ESTILOS.WHITE,
            font=ctk.CTkFont(family="Courier", size=13),
            state="disabled"
        )
        self.txt_formula.pack(fill="both", expand=True, pady=(0, 5))

    def crear_tarjeta(self, padre, titulo):
        tarjeta = ctk.CTkFrame(padre, fg_color=ESTILOS.CARD, corner_radius=10, height=75, border_color=ESTILOS.BORDER, border_width=1)
        tarjeta.pack(fill="x", pady=5)
        tarjeta.pack_propagate(False)

        ctk.CTkLabel(
            tarjeta,
            text=titulo,
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=11, weight="bold")
        ).place(relx=0.5, rely=0.3, anchor="center")

        valor = ctk.CTkLabel(
            tarjeta,
            text="—",
            text_color=ESTILOS.WHITE,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        valor.place(relx=0.5, rely=0.7, anchor="center")
        return valor

    def analizar(self):
        try:
            m = int(self.ent_m.get())
        except ValueError:
            messagebox.showerror("Error de entrada", "El módulo 'm' debe ser un número entero.")
            return

        if m <= 0:
            messagebox.showerror("Error de entrada", "El módulo 'm' debe ser mayor a cero.")
            return

        tipo, formula, pe = analizar_modulo(m)

        self.tar_tipo.configure(text=tipo, text_color=ESTILOS.GREEN)
        self.tar_pe.configure(text=str(pe), text_color=ESTILOS.WHITE)

        self.txt_formula.configure(state="normal")
        self.txt_formula.delete("1.0", "end")
        self.txt_formula.insert("1.0", formula)
        self.txt_formula.configure(state="disabled")

    def limpiar(self):
        self.tar_tipo.configure(text="—", text_color=ESTILOS.WHITE)
        self.tar_pe.configure(text="—", text_color=ESTILOS.WHITE)
        self.txt_formula.configure(state="normal")
        self.txt_formula.delete("1.0", "end")
        self.txt_formula.configure(state="disabled")


if __name__ == "__main__":
    app = PeriodosEsperadosApp()
    app.mainloop()