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
import scipy.stats as stats
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


def cargar_numeros(archivo, n, col, reng):
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


class PruebaKolmogorovApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Prueba de Kolmogorov-Smirnov | Modelado y Simulación")
        self.geometry("1150x750")
        self.configure(fg_color=ESTILOS.BG)
        self.minsize(950, 600)

        self.ruta_csv = RUTA_CSV_PREDETERMINADA

        # Rejilla para sidebar
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.configurar_estilo_tabla()
        self.crear_interfaz()
        self.verificar_archivo_csv()

    def configurar_estilo_tabla(self):
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
        self.ent_n = self.crear_campo(panel_entrada, "N (Cantidad de números):", "20")
        self.ent_alpha = self.crear_campo(panel_entrada, "α (% de significancia, ej. 5):", "5")
        self.ent_col = self.crear_campo(panel_entrada, "Columna en CSV (1-10):", "1")
        self.ent_reng = self.crear_campo(panel_entrada, "Bloque de Renglón (1+):", "1")

        # Botones
        ctk.CTkButton(
            panel_entrada,
            text="EJECUTAR PRUEBA",
            height=45,
            fg_color=ESTILOS.GREEN,
            text_color=ESTILOS.BG,
            hover_color="#00B889",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.ejecutar_prueba
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
            text="PRUEBA ESTADÍSTICA DE KOLMOGOROV-SMIRNOV (K-S)",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ESTILOS.WHITE
        ).grid(row=0, column=0, sticky="w", pady=(10, 2))

        ctk.CTkLabel(
            panel_resultados,
            text="Evalúa la uniformidad comparando la distribución acumulada empírica con la teórica.",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Tarjetas de Resultado Superior
        tarjetas = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        tarjetas.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        tarjetas.grid_columnconfigure(0, weight=1)
        tarjetas.grid_columnconfigure(1, weight=1)
        tarjetas.grid_columnconfigure(2, weight=2)

        self.tar_dmax = self.crear_tarjeta(tarjetas, "D_max Calculado", 0)
        self.tar_dtabla = self.crear_tarjeta(tarjetas, "Estadístico d_tabla", 1)
        self.tar_conclusion = self.crear_tarjeta(tarjetas, "Conclusión Final", 2)

        # Tabview para ver Tabla de Kolmogorov y Números Extraídos
        self.tabview = ctk.CTkTabview(panel_resultados, fg_color=ESTILOS.PANEL, segmented_button_selected_color=ESTILOS.GREEN)
        self.tabview.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        tab_tabla = self.tabview.add("Tabla Kolmogorov")
        tab_numeros = self.tabview.add("Números Extraídos")

        # Configurar Tab 1 (Tabla Kolmogorov)
        tab_tabla.grid_columnconfigure(0, weight=1)
        tab_tabla.grid_rowconfigure(0, weight=1)

        marco_tabla = ctk.CTkFrame(tab_tabla, fg_color="transparent")
        marco_tabla.grid(row=0, column=0, sticky="nsew")
        marco_tabla.grid_rowconfigure(0, weight=1)
        marco_tabla.grid_columnconfigure(0, weight=1)

        columnas = ("i", "xi", "i_sobre_n", "distancia")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings")

        encabezados = {
            "i": "i",
            "xi": "xi (Ordenado)",
            "i_sobre_n": "i/N",
            "distancia": "|i/N - xi|"
        }
        anchos = {"i": 80, "xi": 160, "i_sobre_n": 160, "distancia": 160}

        for col in columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, width=anchos[col], anchor="center")

        barra_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra_y.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")

        # Configurar Tab 2 (Números Extraídos)
        tab_numeros.grid_columnconfigure(0, weight=1)
        tab_numeros.grid_rowconfigure(0, weight=1)
        self.txt_numeros = ctk.CTkTextbox(
            tab_numeros,
            fg_color=ESTILOS.CARD,
            text_color=ESTILOS.WHITE,
            border_color=ESTILOS.BORDER,
            border_width=1,
            font=ctk.CTkFont(family="Courier", size=13)
        )
        self.txt_numeros.grid(row=0, column=0, sticky="nsew")

        # Desarrollo / Veredicto al pie (Tarjeta de Verificación)
        self.veredicto_frame = ctk.CTkFrame(panel_resultados, fg_color=ESTILOS.CARD, height=60, corner_radius=10, border_color=ESTILOS.BORDER, border_width=1)
        self.veredicto_frame.grid(row=4, column=0, sticky="ew", pady=(5, 5))
        self.veredicto_frame.grid_propagate(False)

        self.lbl_desarrollo = ctk.CTkLabel(
            self.veredicto_frame,
            text="Configura los parámetros en el panel izquierdo y haz clic en EJECUTAR PRUEBA.",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ESTILOS.MUTED
        )
        self.lbl_desarrollo.place(relx=0.5, rely=0.5, anchor="center")

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

    def ejecutar_prueba(self):
        self.limpiar_resultados()

        # 1. Validar entradas
        try:
            n = int(self.ent_n.get())
            alpha_pct = float(self.ent_alpha.get())
            col = int(self.ent_col.get())
            reng = int(self.ent_reng.get())
        except ValueError:
            messagebox.showerror("Error de entrada", "Asegúrate de ingresar solo números válidos en los campos.")
            return

        if n <= 0 or alpha_pct <= 0 or alpha_pct >= 100 or col <= 0 or reng <= 0:
            messagebox.showerror("Error de entrada", "Los parámetros N, columna y renglón deben ser mayores a cero. α debe estar entre 0 y 100.")
            return

        # 2. Cargar números
        try:
            numeros = cargar_numeros(self.ruta_csv, n, col, reng)
        except Exception as e:
            messagebox.showerror("Error al cargar archivo", f"No se pudo leer el archivo:\n{str(e)}")
            return

        if not numeros:
            messagebox.showerror("Error", "No se extrajo ningún número. Verifica que la columna y el renglón de inicio sean correctos.")
            return

        if len(numeros) < n:
            messagebox.showwarning("Advertencia", f"Solo se pudieron cargar {len(numeros)} números en lugar de los {n} solicitados.")
            n = len(numeros)

        # 3. Mostrar números extraídos (Originales)
        self.txt_numeros.configure(state="normal")
        self.txt_numeros.delete("1.0", "end")
        for i in range(0, len(numeros), 5):
            grupo = numeros[i:i+5]
            grupo_str = "   ".join([f"{num:.5f}" for num in grupo])
            self.txt_numeros.insert("end", f"[{i+1:02d}-{min(i+5, len(numeros)):02d}]:  {grupo_str}\n")
        self.txt_numeros.configure(state="disabled")

        # 4. Kolmogorov-Smirnov
        numeros_ordenados = sorted(numeros)
        d_max = 0

        for i in range(n):
            posicion = i + 1
            i_sobre_n = posicion / n
            distancia = abs(i_sobre_n - numeros_ordenados[i])

            if distancia > d_max:
                d_max = distancia

            self.tabla.insert(
                "", "end",
                values=(
                    posicion,
                    f"{numeros_ordenados[i]:.5f}",
                    f"{i_sobre_n:.6f}",
                    f"{distancia:.6f}"
                )
            )

        # Buscar en Tablas
        alfa = alpha_pct / 100.0
        d_tabla = stats.ksone.ppf(1 - alfa, n)

        # Aceptación
        if d_max < d_tabla:
            conclusion = "Uniformes (Aceptados) ✅"
            color_conclusion = ESTILOS.GREEN
            self.veredicto_frame.configure(fg_color="#0A3D2E", border_color=ESTILOS.GREEN, border_width=2)
        else:
            conclusion = "No Uniformes (Rechazados) ❌"
            color_conclusion = ESTILOS.RED
            self.veredicto_frame.configure(fg_color="#3D0A0A", border_color=ESTILOS.RED, border_width=2)

        # Actualizar Tarjetas
        self.tar_dmax.configure(text=f"{d_max:.6f}")
        self.tar_dtabla.configure(text=f"{d_tabla:.6f}")
        self.tar_conclusion.configure(text=conclusion, text_color=color_conclusion)

        # Actualizar desarrollo
        self.lbl_desarrollo.configure(
            text=f"Hipótesis Aceptada: D_max = {d_max:.6f} < d_tabla = {d_tabla:.6f}" if d_max < d_tabla else f"Hipótesis Rechazada: D_max = {d_max:.6f} >= d_tabla = {d_tabla:.6f}",
            text_color=color_conclusion
        )

    def limpiar_resultados(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.txt_numeros.configure(state="normal")
        self.txt_numeros.delete("1.0", "end")
        self.txt_numeros.configure(state="disabled")

        self.tar_dmax.configure(text="—")
        self.tar_dtabla.configure(text="—")
        self.tar_conclusion.configure(text="—", text_color=ESTILOS.WHITE)
        self.veredicto_frame.configure(fg_color=ESTILOS.CARD, border_color=ESTILOS.BORDER, border_width=1)
        self.lbl_desarrollo.configure(
            text="Configura los parámetros en el panel izquierdo y haz clic en EJECUTAR PRUEBA.",
            text_color=ESTILOS.MUTED
        )

    def limpiar(self):
        self.limpiar_resultados()
        self.verificar_archivo_csv()


if __name__ == "__main__":
    app = PruebaKolmogorovApp()
    app.mainloop()