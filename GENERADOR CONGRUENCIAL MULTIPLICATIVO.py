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
import ESTILOS
import math
from tkinter import ttk, messagebox

ESTILOS.aplicar_tema()


def analizar_modulo(m):
    """
    Determina si el módulo es Binario, Decimal o Especial,
    y calcula su Periodo Esperado (P.E.).
    """
    if m <= 0:
        return "Inválido", 0

    # Detección de Binario (Potencia de 2)
    if (m & (m - 1) == 0) and m > 0:
        return "Binario (Potencia de 2)", m // 4

    # Detección de Decimal (Potencia de 10)
    try:
        log10 = math.log10(m)
        if log10.is_integer():
            d = int(log10)
            if d >= 5:
                pe = 5 * (10 ** (d - 2))
            else:
                # Cálculo de lambda para d < 5
                l5 = (5 ** (d - 1)) * 4
                l2 = 2 if d in (1, 2) else 2 ** (d - 2)
                pe = math.lcm(l5, l2)  # Mínimo Común Múltiplo
            return "Decimal (Potencia de 10)", pe
    except Exception:
        pass

    return "Especial", m


def ejecutar_generador_multiplicativo(a, x0, m):
    """
    Ejecuta el algoritmo del Generador Congruencial Multiplicativo.
    Fórmula: X_{n+1} = (a * X_n) mod m
    """
    tipo, pe = analizar_modulo(m)
    filas = []
    xn = x0

    for i in range(pe):
        resultado_operacion = (a * xn)
        resultado_division = resultado_operacion // m
        xn_siguiente = resultado_operacion % m
        ui = xn_siguiente / m

        formula_str = f"{resultado_division} + {xn_siguiente}/{m}"
        filas.append(
            (
                i + 1,
                xn,
                formula_str,
                xn_siguiente,
                f"{ui:.6f}"
            )
        )
        xn = xn_siguiente

    return tipo, pe, filas


class GeneradorMultiplicativoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Generador Congruencial Multiplicativo | Modelado y Simulación")
        self.geometry("1100x700")
        self.configure(fg_color=ESTILOS.BG)
        self.minsize(900, 600)

        # Rejilla para sidebar
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.configurar_estilo_tabla()
        self.crear_interfaz()

    def configurar_estilo_tabla(self):
        ESTILOS.configurar_tabla()

    def crear_interfaz(self):
        # ── PANEL IZQUIERDO (Sidebar - Datos) ──
        panel_datos = ctk.CTkScrollableFrame(self, width=280, fg_color=ESTILOS.PANEL, corner_radius=0)
        panel_datos.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            panel_datos,
            text="Parámetros",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ESTILOS.WHITE
        ).pack(pady=(20, 20), padx=20, anchor="w")

        # Campos de entrada
        self.ent_a = self.crear_campo(panel_datos, "Multiplicador (a):", "5")
        self.ent_x0 = self.crear_campo(panel_datos, "Semilla inicial (x0):", "5")
        self.ent_m = self.crear_campo(panel_datos, "Módulo (m):", "32")

        # Botones
        ctk.CTkButton(
            panel_datos,
            text="GENERAR NÚMEROS",
            height=45,
            fg_color=ESTILOS.GREEN,
            text_color=ESTILOS.BG,
            hover_color="#00B889",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.generar
        ).pack(fill="x", padx=20, pady=(25, 10))

        ctk.CTkButton(
            panel_datos,
            text="LIMPIAR",
            height=35,
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
        panel_resultados.grid_rowconfigure(3, weight=1)

        # Encabezado
        ctk.CTkLabel(
            panel_resultados,
            text="GENERADOR CONGRUENCIAL MULTIPLICATIVO",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ESTILOS.WHITE
        ).grid(row=0, column=0, sticky="w", pady=(10, 2))

        ctk.CTkLabel(
            panel_resultados,
            text="Fórmula: Xn+1 = (a * Xn) mod m  •  Ui = Xn+1 / m",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Tarjetas de Información del Módulo
        tarjetas = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        tarjetas.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        tarjetas.grid_columnconfigure(0, weight=1)
        tarjetas.grid_columnconfigure(1, weight=1)

        self.tar_tipo = self.crear_tarjeta(tarjetas, "Tipo de Módulo", 0)
        self.tar_pe = self.crear_tarjeta(tarjetas, "Periodo Esperado (P.E.)", 1)

        # Tabla (Treeview)
        marco_tabla = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        marco_tabla.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        marco_tabla.grid_rowconfigure(0, weight=1)
        marco_tabla.grid_columnconfigure(0, weight=1)

        columnas = ("i", "xn", "formula", "xn_siguiente", "ui")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings")

        encabezados = {
            "i": "i (Iteración)",
            "xn": "Xn",
            "formula": "Fórmula (q + r/m)",
            "xn_siguiente": "Xn+1",
            "ui": "Ui (Número pseudoaleatorio)"
        }
        anchos = {
            "i": 90,
            "xn": 110,
            "formula": 200,
            "xn_siguiente": 110,
            "ui": 185
        }

        for col in columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, width=anchos[col], anchor="center")

        barra_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        barra_x = ttk.Scrollbar(marco_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")

        # Resumen al pie
        self.veredicto_frame = ctk.CTkFrame(panel_resultados, fg_color=ESTILOS.CARD, height=60, corner_radius=10, border_color=ESTILOS.BORDER, border_width=1)
        self.veredicto_frame.grid(row=4, column=0, sticky="ew", pady=(5, 5))
        self.veredicto_frame.grid_propagate(False)

        self.lbl_resumen = ctk.CTkLabel(
            self.veredicto_frame,
            text="Ingresa los parámetros y haz clic en GENERAR NÚMEROS.",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ESTILOS.MUTED
        )
        self.lbl_resumen.place(relx=0.5, rely=0.5, anchor="center")

    def crear_campo(self, padre, texto, valor):
        ctk.CTkLabel(
            padre,
            text=texto,
            anchor="w",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=20, pady=(10, 2))

        entrada = ctk.CTkEntry(
            padre,
            height=34,
            fg_color=ESTILOS.CARD,
            border_color=ESTILOS.BORDER,
            text_color=ESTILOS.WHITE
        )
        entrada.pack(fill="x", padx=20, pady=(0, 5))
        entrada.insert(0, valor)
        return entrada

    def crear_tarjeta(self, padre, titulo, columna):
        tarjeta = ctk.CTkFrame(padre, fg_color=ESTILOS.CARD, corner_radius=10, height=80, border_color=ESTILOS.BORDER, border_width=1)
        tarjeta.grid(row=0, column=columna, sticky="ew", padx=5)
        tarjeta.grid_propagate(False)

        ctk.CTkLabel(
            tarjeta,
            text=titulo,
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=12, weight="bold")
        ).place(relx=0.5, rely=0.3, anchor="center")

        valor = ctk.CTkLabel(
            tarjeta,
            text="—",
            text_color=ESTILOS.WHITE,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        valor.place(relx=0.5, rely=0.7, anchor="center")
        return valor

    def generar(self):
        self.limpiar()

        try:
            a = int(self.ent_a.get())
            x0 = int(self.ent_x0.get())
            m = int(self.ent_m.get())
        except ValueError:
            messagebox.showerror("Error de entrada", "Todos los parámetros deben ser números enteros.")
            return

        if a <= 0 or x0 <= 0 or m <= 0:
            messagebox.showerror("Error de entrada", "Todos los parámetros deben ser mayores a cero.")
            return

        tipo, pe, filas = ejecutar_generador_multiplicativo(a, x0, m)

        self.tar_tipo.configure(text=tipo)
        self.tar_pe.configure(text=str(pe))

        for fila in filas:
            self.tabla.insert("", "end", values=fila)

        self.veredicto_frame.configure(fg_color="#0A3D2E", border_color=ESTILOS.GREEN, border_width=2)
        self.lbl_resumen.configure(
            text=f"Periodo esperado completado ({pe} iteraciones) | Semilla x0 = {x0} | Último residuo xn = {filas[-1][3] if filas else x0}",
            text_color=ESTILOS.GREEN
        )

    def limpiar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.tar_tipo.configure(text="—")
        self.tar_pe.configure(text="—")
        self.veredicto_frame.configure(fg_color=ESTILOS.CARD, border_color=ESTILOS.BORDER, border_width=1)
        self.lbl_resumen.configure(
            text="Ingresa los parámetros y haz clic en GENERAR NÚMEROS.",
            text_color=ESTILOS.MUTED
        )


if __name__ == "__main__":
    app = GeneradorMultiplicativoApp()
    app.mainloop()