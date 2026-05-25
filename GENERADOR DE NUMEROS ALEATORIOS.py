
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
import random
import customtkinter as ctk
import ESTILOS
from tkinter import ttk, messagebox, filedialog

ESTILOS.aplicar_tema()

DIRECTORIO_PROGRAMA = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV_PREDETERMINADA = os.path.join(
    DIRECTORIO_PROGRAMA,
    "DATOS",
    "NUMEROS_ALEATORIOS.csv"
)


class GeneradorNumerosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Generador de Números Aleatorios | Modelado y Simulación")
        self.geometry("1100x700")
        self.state('zoomed')
        self.configure(fg_color=ESTILOS.BG)
        self.minsize(900, 580)

        self.ruta_guardado = RUTA_CSV_PREDETERMINADA

        # Rejilla para sidebar
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.configurar_estilo_tabla()
        self.crear_interfaz()
        self.actualizar_lbl_ruta()

    def configurar_estilo_tabla(self):
        ESTILOS.configurar_tabla()

    def crear_interfaz(self):
        # ── PANEL IZQUIERDO (Sidebar - Entrada) ──
        panel_entrada = ctk.CTkScrollableFrame(self, width=280, fg_color=ESTILOS.PANEL, corner_radius=0)
        panel_entrada.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            panel_entrada,
            text="Configuración",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ESTILOS.WHITE
        ).pack(pady=(20, 10), padx=20, anchor="w")

        # Campos de dimensión
        self.ent_filas = self.crear_campo(panel_entrada, "Cantidad de filas:", "40")
        self.ent_columnas = self.crear_campo(panel_entrada, "Cantidad de columnas:", "10")
        self.ent_digitos = self.crear_campo(panel_entrada, "Cantidad de dígitos por número:", "5")

        # Configuración de Ruta
        ctk.CTkLabel(
            panel_entrada,
            text="Ruta de guardado:",
            anchor="w",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=20, pady=(8, 2))

        self.lbl_ruta = ctk.CTkLabel(
            panel_entrada,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ESTILOS.WHITE,
            wraplength=240,
            justify="center"
        )
        self.lbl_ruta.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkButton(
            panel_entrada,
            text="EXAMINAR RUTA...",
            height=32,
            fg_color=ESTILOS.CARD,
            text_color=ESTILOS.WHITE,
            border_color=ESTILOS.BORDER,
            border_width=1,
            hover_color=ESTILOS.PANEL,
            command=self.examinar_ruta
        ).pack(fill="x", padx=20, pady=(0, 15))

        # Botones de Acción
        ctk.CTkButton(
            panel_entrada,
            text="GENERAR Y GUARDAR",
            height=45,
            fg_color=ESTILOS.GREEN,
            text_color=ESTILOS.BG,
            hover_color="#00B889",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.generar_y_guardar
        ).pack(fill="x", padx=20, pady=(25, 10))

        ctk.CTkButton(
            panel_entrada,
            text="LIMPIAR PREVIO",
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
            text="GENERADOR DE NÚMEROS ALEATORIOS",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ESTILOS.WHITE
        ).grid(row=0, column=0, sticky="w", pady=(10, 2))

        ctk.CTkLabel(
            panel_resultados,
            text="Genera una cuadrícula de números aleatorios uniformes y guárdala en formato de 5 dígitos para simulaciones.",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Tarjetas de Información Superior
        tarjetas = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        tarjetas.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        tarjetas.grid_columnconfigure(0, weight=1)
        tarjetas.grid_columnconfigure(1, weight=1)

        self.tar_total = self.crear_tarjeta(tarjetas, "Total de Números Generados", 0)
        self.tar_archivo = self.crear_tarjeta(tarjetas, "Estado del Archivo", 1)

        # Tabla de vista previa
        self.marco_tabla = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        self.marco_tabla.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        self.marco_tabla.grid_rowconfigure(0, weight=1)
        self.marco_tabla.grid_columnconfigure(0, weight=1)

        # Tabla vacía inicial
        self.tabla = None
        self.inicializar_tabla_columnas(10)

        # Resumen al pie (Tarjeta de Verificación)
        self.veredicto_frame = ctk.CTkFrame(panel_resultados, fg_color=ESTILOS.CARD, height=60, corner_radius=10, border_color=ESTILOS.BORDER, border_width=1)
        self.veredicto_frame.grid(row=4, column=0, sticky="ew", pady=(5, 5))
        self.veredicto_frame.grid_propagate(False)

        self.lbl_resumen = ctk.CTkLabel(
            self.veredicto_frame,
            text="Configura los parámetros y haz clic en GENERAR Y GUARDAR.",
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

    def actualizar_lbl_ruta(self):
        nombre_archivo = os.path.basename(self.ruta_guardado)
        directorio = os.path.basename(os.path.dirname(self.ruta_guardado))
        self.lbl_ruta.configure(text=f"{directorio}/{nombre_archivo}")

    def examinar_ruta(self):
        ruta = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(self.ruta_guardado),
            initialfile=os.path.basename(self.ruta_guardado),
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if ruta:
            self.ruta_guardado = ruta
            self.actualizar_lbl_ruta()

    def inicializar_tabla_columnas(self, num_columnas):
        if self.tabla is not None:
            for widget in self.marco_tabla.winfo_children():
                widget.destroy()

        columnas = ["fila"] + [f"col_{i+1}" for i in range(num_columnas)]
        self.tabla = ttk.Treeview(self.marco_tabla, columns=columnas, show="headings")

        self.tabla.heading("fila", text="Fila")
        self.tabla.column("fila", width=70, anchor="center")

        for i in range(num_columnas):
            col_id = f"col_{i+1}"
            self.tabla.heading(col_id, text=f"Col {i+1}")
            self.tabla.column(col_id, width=80, anchor="center")

        barra_y = ttk.Scrollbar(self.marco_tabla, orient="vertical", command=self.tabla.yview)
        barra_x = ttk.Scrollbar(self.marco_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")

    def generar_y_guardar(self):
        self.limpiar_resultados()

        try:
            filas_num = int(self.ent_filas.get())
            columnas_num = int(self.ent_columnas.get())
            digitos_num = int(self.ent_digitos.get())
        except ValueError:
            messagebox.showerror("Error de entrada", "Las filas, columnas y dígitos deben ser números enteros.")
            return

        if filas_num <= 0 or columnas_num <= 0 or digitos_num <= 0:
            messagebox.showerror("Error de entrada", "Todos los parámetros deben ser mayores a cero.")
            return

        if digitos_num > 10:
            messagebox.showerror("Error de entrada", "El número máximo de dígitos es 10.")
            return

        matriz = []
        limite_max = (10 ** digitos_num) - 1

        for _ in range(filas_num):
            fila = []
            for _ in range(columnas_num):
                num_int = random.randint(0, limite_max)
                num_str = f"{num_int:0{digitos_num}d}"
                fila.append(num_str)
            matriz.append(fila)

        try:
            directorio = os.path.dirname(self.ruta_guardado)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio, exist_ok=True)

            with open(self.ruta_guardado, "w", newline="", encoding="utf-8") as archivo:
                escritor = csv.writer(archivo)
                escritor.writerows(matriz)
        except Exception as e:
            messagebox.showerror("Error al guardar archivo", f"No se pudo guardar el archivo CSV:\n{str(e)}")
            return

        self.inicializar_tabla_columnas(columnas_num)

        for r_idx, fila in enumerate(matriz[:30]):
            valores = [r_idx + 1] + fila
            self.tabla.insert("", "end", values=valores)

        total_numeros = filas_num * columnas_num
        self.tar_total.configure(text=str(total_numeros))
        self.tar_archivo.configure(text="Guardado ", text_color=ESTILOS.GREEN)

        self.veredicto_frame.configure(fg_color="#0A3D2E", border_color=ESTILOS.GREEN, border_width=2)
        self.lbl_resumen.configure(
            text=f"Generación exitosa: {filas_num}x{columnas_num} ({total_numeros} números) guardados en CSV",
            text_color=ESTILOS.GREEN
        )

    def limpiar_resultados(self):
        if self.tabla is not None:
            for item in self.tabla.get_children():
                self.tabla.delete(item)

        self.tar_total.configure(text="—")
        self.tar_archivo.configure(text="—", text_color=ESTILOS.WHITE)
        self.veredicto_frame.configure(fg_color=ESTILOS.CARD, border_color=ESTILOS.BORDER, border_width=1)
        self.lbl_resumen.configure(
            text="Configura los parámetros y haz clic en GENERAR Y GUARDAR.",
            text_color=ESTILOS.MUTED
        )

    def limpiar(self):
        self.limpiar_resultados()
        self.actualizar_lbl_ruta()


if __name__ == "__main__":
    app = GeneradorNumerosApp()
    app.mainloop()