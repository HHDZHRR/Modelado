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

import csv
import os
import math
import customtkinter as ctk
import ESTILOS
from tkinter import ttk, messagebox

ESTILOS.aplicar_tema()

DIRECTORIO_PROGRAMA = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV_PREDETERMINADA = os.path.join(
    DIRECTORIO_PROGRAMA,
    "DATOS",
    "NUMEROS_ALEATORIOS.csv"
)


def cargar_datos(archivo, n, col, reng):
    """
    Carga n números del archivo CSV en la columna 'col' y empezando
    desde la fila 'reng' (bloques de 5 filas).
    """
    numeros = []
    col_idx = col - 1
    fila_inicio = (reng - 1) * 5

    if not os.path.exists(archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {archivo}")

    with open(archivo, 'r', encoding='utf-8-sig') as f:
        lector = csv.reader(f)
        filas = list(lector)

        for i in range(fila_inicio, min(fila_inicio + n, len(filas))):
            if col_idx < len(filas[i]):
                valor_texto = filas[i][col_idx].strip()
                if not valor_texto:
                    continue
                if "." in valor_texto:
                    valor_decimal = float(valor_texto)
                else:
                    valor_decimal = float("0." + valor_texto)
                numeros.append(valor_decimal)
    return numeros


class GeneracionPoissonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Generación Variable Poisson | Modelado y Simulación")
        self.geometry("1150x750")
        self.state('zoomed')
        self.configure(fg_color=ESTILOS.BG)
        self.minsize(950, 600)

        self.ruta_csv = RUTA_CSV_PREDETERMINADA

        # Rejilla para sidebar
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.configurar_estilos_tablas()
        self.crear_interfaz()
        self.verificar_archivo_csv()

    def configurar_estilos_tablas(self):
        ESTILOS.configurar_tabla()

    def verificar_archivo_csv(self):
        if os.path.exists(self.ruta_csv):
            nombre_archivo = os.path.basename(self.ruta_csv)
            self.lbl_estado_csv.configure(
                text=f"CSV detectado: {nombre_archivo}",
                text_color=ESTILOS.GREEN
            )
        else:
            self.lbl_estado_csv.configure(
                text="Archivo CSV no detectado",
                text_color=ESTILOS.AMBER
            )

    def seleccionar_csv(self):
        from tkinter import filedialog
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de números aleatorios",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.ruta_csv = archivo
            self.verificar_archivo_csv()

    def crear_interfaz(self):
        # ── PANEL IZQUIERDO (Sidebar - Entrada) ──
        panel_entrada = ctk.CTkScrollableFrame(self, width=280, fg_color=ESTILOS.PANEL, corner_radius=0)
        panel_entrada.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            panel_entrada,
            text="Parámetros",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ESTILOS.WHITE
        ).pack(pady=(20, 10), padx=20, anchor="w")

        # Estado del CSV
        self.lbl_estado_csv = ctk.CTkLabel(
            panel_entrada,
            text="Verificando archivo...",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ESTILOS.MUTED,
            wraplength=240,
            justify="center"
        )
        self.lbl_estado_csv.pack(fill="x", padx=20, pady=(0, 5))

        self.btn_seleccionar_csv = ctk.CTkButton(
            panel_entrada,
            text="SELECCIONAR CSV",
            height=30,
            fg_color=ESTILOS.CARD,
            text_color=ESTILOS.WHITE,
            border_color=ESTILOS.BORDER,
            border_width=1,
            hover_color=ESTILOS.PANEL,
            command=self.seleccionar_csv
        )
        self.btn_seleccionar_csv.pack(fill="x", padx=20, pady=(0, 15))

        # Parámetros numéricos
        self.ent_n = self.crear_campo(panel_entrada, "N (Cantidad a generar):", "20")
        self.ent_lambda = self.crear_campo(panel_entrada, "Media de Poisson (λ):", "2")
        self.ent_col = self.crear_campo(panel_entrada, "Columna en CSV (1-10):", "1")
        self.ent_reng = self.crear_campo(panel_entrada, "Bloque de Renglón (1+):", "1")

        # Botones
        ctk.CTkButton(
            panel_entrada,
            text="GENERAR VARIABLES",
            height=45,
            fg_color=ESTILOS.GREEN,
            text_color=ESTILOS.BG,
            hover_color="#00B889",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.generar
        ).pack(fill="x", padx=20, pady=(25, 10))

        ctk.CTkButton(
            panel_entrada,
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
        panel_resultados.grid_rowconfigure(2, weight=1)

        # Encabezado
        ctk.CTkLabel(
            panel_resultados,
            text="GENERACIÓN DE VARIABLES ALEATORIAS POISSON",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ESTILOS.WHITE
        ).grid(row=0, column=0, sticky="w", pady=(10, 2))

        ctk.CTkLabel(
            panel_resultados,
            text="Fórmula de probabilidad: p(x) = (e^-λ * λ^x) / x!  •  Generado mediante rangos acumulados.",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Tarjetas de Resultado Superior
        tarjetas = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        tarjetas.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        tarjetas.grid_columnconfigure(0, weight=1)
        tarjetas.grid_columnconfigure(1, weight=1)
        tarjetas.grid_columnconfigure(2, weight=1)

        self.tar_demanda = self.crear_tarjeta(tarjetas, "Demanda Total (Σ X)", 0)
        self.tar_promedio = self.crear_tarjeta(tarjetas, "Promedio (x̄)", 1)
        self.tar_n = self.crear_tarjeta(tarjetas, "Muestra Generada (N)", 2)

        # Tabview para ver Simulación y Tabla de Rangos
        self.tabview = ctk.CTkTabview(panel_resultados, fg_color=ESTILOS.PANEL, segmented_button_selected_color=ESTILOS.GREEN)
        self.tabview.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        tab_simulacion = self.tabview.add("Simulación de Variables")
        tab_rangos = self.tabview.add("Tabla de Rangos F(xi)")

        # Configurar Tab 1 (Simulación)
        tab_simulacion.grid_columnconfigure(0, weight=1)
        tab_simulacion.grid_rowconfigure(0, weight=1)

        marco_tab_sim = ctk.CTkFrame(tab_simulacion, fg_color="transparent")
        marco_tab_sim.grid(row=0, column=0, sticky="nsew")
        marco_tab_sim.grid_rowconfigure(0, weight=1)
        marco_tab_sim.grid_columnconfigure(0, weight=1)

        self.tabla_simulacion = ttk.Treeview(marco_tab_sim, columns=("i", "r", "x"), show="headings")
        self.tabla_simulacion.heading("i", text="i (Índice)")
        self.tabla_simulacion.column("i", width=100, anchor="center")
        self.tabla_simulacion.heading("r", text="R (Número Uniforme)")
        self.tabla_simulacion.column("r", width=220, anchor="center")
        self.tabla_simulacion.heading("x", text="X (Variable Poisson)")
        self.tabla_simulacion.column("x", width=250, anchor="center")

        barra_y_sim = ttk.Scrollbar(marco_tab_sim, orient="vertical", command=self.tabla_simulacion.yview)
        self.tabla_simulacion.configure(yscrollcommand=barra_y_sim.set)
        self.tabla_simulacion.grid(row=0, column=0, sticky="nsew")
        barra_y_sim.grid(row=0, column=1, sticky="ns")

        # Configurar Tab 2 (Tabla de Rangos)
        tab_rangos.grid_columnconfigure(0, weight=1)
        tab_rangos.grid_rowconfigure(0, weight=1)

        marco_tab_ran = ctk.CTkFrame(tab_rangos, fg_color="transparent")
        marco_tab_ran.grid(row=0, column=0, sticky="nsew")
        marco_tab_ran.grid_rowconfigure(0, weight=1)
        marco_tab_ran.grid_columnconfigure(0, weight=1)

        self.tabla_rangos = ttk.Treeview(marco_tab_ran, columns=("x", "f_x", "f_acum"), show="headings")
        self.tabla_rangos.heading("x", text="X (Demanda)")
        self.tabla_rangos.column("x", width=120, anchor="center")
        self.tabla_rangos.heading("f_x", text="Probabilidad p(xi)")
        self.tabla_rangos.column("f_x", width=220, anchor="center")
        self.tabla_rangos.heading("f_acum", text="Probabilidad Acumulada F(xi)")
        self.tabla_rangos.column("f_acum", width=250, anchor="center")

        barra_y_ran = ttk.Scrollbar(marco_tab_ran, orient="vertical", command=self.tabla_rangos.yview)
        self.tabla_rangos.configure(yscrollcommand=barra_y_ran.set)
        self.tabla_rangos.grid(row=0, column=0, sticky="nsew")
        barra_y_ran.grid(row=0, column=1, sticky="ns")

        # Texto de resumen inferior (Tarjeta de Verificación)
        self.veredicto_frame = ctk.CTkFrame(panel_resultados, fg_color=ESTILOS.CARD, height=60, corner_radius=10, border_color=ESTILOS.BORDER, border_width=1)
        self.veredicto_frame.grid(row=4, column=0, sticky="ew", pady=(5, 5))
        self.veredicto_frame.grid_propagate(False)

        self.lbl_resumen = ctk.CTkLabel(
            self.veredicto_frame,
            text="Configura los parámetros en el panel izquierdo y haz clic en GENERAR VARIABLES.",
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
            font=ctk.CTkFont(size=11, weight="bold")
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
        self.limpiar_resultados()

        # 1. Validar entradas
        try:
            n = int(self.ent_n.get())
            lam = float(self.ent_lambda.get())
            col = int(self.ent_col.get())
            reng = int(self.ent_reng.get())
        except ValueError:
            messagebox.showerror("Error de entrada", "Asegúrate de ingresar solo números válidos en los campos.")
            return

        if n <= 0 or lam <= 0 or col <= 0 or reng <= 0:
            messagebox.showerror("Error de entrada", "Todos los parámetros deben ser mayores a cero.")
            return

        # 2. Construir tabla de rangos
        tabla_rangos = []
        x_i = 0
        f_acum = 0.0

        while f_acum < 0.99995:
            try:
                prob = (math.exp(-lam) * (lam ** x_i)) / math.factorial(x_i)
            except OverflowError:
                break
            f_acum += prob
            tabla_rangos.append((x_i, f_acum))
            self.tabla_rangos.insert(
                "", "end",
                values=(
                    x_i,
                    f"{prob:.6f}",
                    f"{f_acum:.6f}"
                )
            )
            x_i += 1

        # 3. Cargar datos del CSV
        try:
            nums_r = cargar_datos(self.ruta_csv, n, col, reng)
        except Exception as e:
            messagebox.showerror("Error al cargar archivo", f"No se pudo leer el archivo:\n{str(e)}")
            return

        if not nums_r:
            messagebox.showerror("Error", "No se extrajo ningún número. Verifica que la columna y el renglón de inicio sean correctos.")
            return

        if len(nums_r) < n:
            messagebox.showwarning("Advertencia", f"Solo se pudieron cargar {len(nums_r)} números en lugar de los {n} solicitados.")
            n = len(nums_r)

        # 4. Asignación de variables de Poisson
        resultados = []
        for i, r in enumerate(nums_r):
            valor_x = 0
            for val, acum in tabla_rangos:
                if r < acum:
                    valor_x = val
                    break
            resultados.append(valor_x)
            self.tabla_simulacion.insert("", "end", values=(i + 1, f"{r:.5f}", valor_x))

        # 5. Totales
        demanda_total = sum(resultados)
        promedio = demanda_total / n

        self.tar_demanda.configure(text=str(demanda_total))
        self.tar_promedio.configure(text=f"{promedio:.4f}")
        self.tar_n.configure(text=str(n))

        self.veredicto_frame.configure(fg_color="#0A3D2E", border_color=ESTILOS.GREEN, border_width=2)
        self.lbl_resumen.configure(
            text=f"Variables de Poisson generadas con éxito (λ = {lam}) | Demanda total = {demanda_total}",
            text_color=ESTILOS.GREEN
        )

    def limpiar_resultados(self):
        for item in self.tabla_simulacion.get_children():
            self.tabla_simulacion.delete(item)
        for item in self.tabla_rangos.get_children():
            self.tabla_rangos.delete(item)

        self.tar_demanda.configure(text="—")
        self.tar_promedio.configure(text="—")
        self.tar_n.configure(text="—")
        self.veredicto_frame.configure(fg_color=ESTILOS.CARD, border_color=ESTILOS.BORDER, border_width=1)
        self.lbl_resumen.configure(
            text="Configura los parámetros en el panel izquierdo y haz clic en GENERAR VARIABLES.",
            text_color=ESTILOS.MUTED
        )

    def limpiar(self):
        self.limpiar_resultados()
        self.verificar_archivo_csv()


if __name__ == "__main__":
    app = GeneracionPoissonApp()
    app.mainloop()