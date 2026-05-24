import csv
import os
import math
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


class PruebaPromedioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Prueba de Promedio | Modelado y Simulación")
        self.geometry("1100x700")
        self.configure(fg_color=ESTILOS.BG)
        self.minsize(900, 580)

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
            self.lbl_estado_csv.configure(
                text="Archivo CSV detectado correctamente.",
                text_color=ESTILOS.GREEN
            )
        else:
            self.lbl_estado_csv.configure(
                text="Archivo CSV no detectado en DATOS/NUMEROS_ALEATORIOS.csv",
                text_color=ESTILOS.AMBER
            )

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
        self.lbl_estado_csv.pack(fill="x", padx=20, pady=(0, 15))

        # Parámetros numéricos
        self.ent_n = self.crear_campo(panel_entrada, "N (Cantidad de números):", "40")
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
            text="PRUEBA ESTADÍSTICA DE PROMEDIO",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ESTILOS.WHITE
        ).grid(row=0, column=0, sticky="w", pady=(10, 2))

        ctk.CTkLabel(
            panel_resultados,
            text="Verifica si el promedio de los números generados se desvía significativamente de 0.5.",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Tarjetas de Resultado Superior
        tarjetas = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        tarjetas.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        tarjetas.grid_columnconfigure(0, weight=1)
        tarjetas.grid_columnconfigure(1, weight=1)
        tarjetas.grid_columnconfigure(2, weight=1)
        tarjetas.grid_columnconfigure(3, weight=2)

        self.tar_promedio = self.crear_tarjeta(tarjetas, "Promedio (x̄)", 0)
        self.tar_z0 = self.crear_tarjeta(tarjetas, "Z0 Calculado", 1)
        self.tar_ztabla = self.crear_tarjeta(tarjetas, "Estadístico Z_tablas", 2)
        self.tar_conclusion = self.crear_tarjeta(tarjetas, "Conclusión Final", 3)

        # Tabview para ver Tabla de Números y Detalle Matemático
        self.tabview = ctk.CTkTabview(panel_resultados, fg_color=ESTILOS.PANEL, segmented_button_selected_color=ESTILOS.GREEN)
        self.tabview.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        tab_numeros = self.tabview.add("Números Extraídos")
        tab_calculos = self.tabview.add("Desarrollo de Fórmulas")

        # Configurar Tab 1 (Tabla Números Extraídos)
        tab_numeros.grid_columnconfigure(0, weight=1)
        tab_numeros.grid_rowconfigure(0, weight=1)

        marco_tabla = ctk.CTkFrame(tab_numeros, fg_color="transparent")
        marco_tabla.grid(row=0, column=0, sticky="nsew")
        marco_tabla.grid_rowconfigure(0, weight=1)
        marco_tabla.grid_columnconfigure(0, weight=1)

        columnas = ("i", "xi")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings")

        self.tabla.heading("i", text="i (Iteración)")
        self.tabla.column("i", width=120, anchor="center")
        self.tabla.heading("xi", text="xi (Valor rectangular)")
        self.tabla.column("xi", width=250, anchor="center")

        barra_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra_y.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")

        # Configurar Tab 2 (Desarrollo Fórmulas)
        tab_calculos.grid_columnconfigure(0, weight=1)
        tab_calculos.grid_rowconfigure(0, weight=1)
        self.txt_calculos = ctk.CTkTextbox(
            tab_calculos,
            fg_color=ESTILOS.CARD,
            text_color=ESTILOS.WHITE,
            border_color=ESTILOS.BORDER,
            border_width=1,
            font=ctk.CTkFont(family="Courier", size=13)
        )
        self.txt_calculos.grid(row=0, column=0, sticky="nsew")

        # Desarrollo rápido abajo (Tarjeta de Verificación)
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

        # 3. Insertar números en la tabla
        for i, val in enumerate(numeros):
            self.tabla.insert("", "end", values=(i + 1, f"{val:.5f}"))

        # 4. Cálculos estadísticos
        suma_total = sum(numeros)
        promedio = suma_total / n
        z_0 = abs((promedio - 0.5) * math.sqrt(n) / math.sqrt(1 / 12))

        alfa = alpha_pct / 100.0
        alfa_medios = alfa / 2
        z_tabla = abs(stats.norm.ppf(alfa_medios))

        # Aceptación
        if z_0 < z_tabla:
            conclusion = "Uniformes (Aceptados) ✅"
            color_conclusion = ESTILOS.GREEN
            self.veredicto_frame.configure(fg_color="#0A3D2E", border_color=ESTILOS.GREEN, border_width=2)
        else:
            conclusion = "No Uniformes (Rechados) ❌"
            color_conclusion = ESTILOS.RED
            self.veredicto_frame.configure(fg_color="#3D0A0A", border_color=ESTILOS.RED, border_width=2)

        # Actualizar Tarjetas
        self.tar_promedio.configure(text=f"{promedio:.5f}")
        self.tar_z0.configure(text=f"{z_0:.5f}")
        self.tar_ztabla.configure(text=f"{z_tabla:.3f}")
        self.tar_conclusion.configure(text=conclusion, text_color=color_conclusion)

        # Actualizar Tab 2 (Detalle Fórmulas)
        self.txt_calculos.configure(state="normal")
        self.txt_calculos.delete("1.0", "end")
        desarrollo_completo = (
            f"=== DESARROLLO DE LA PRUEBA DE PROMEDIO ===\n\n"
            f"1. Tamaño de la muestra (N): {n}\n"
            f"2. Nivel de significancia (α): {alfa:.4f} ({alpha_pct}%)\n"
            f"3. Suma total de los números: {suma_total:.5f}\n"
            f"4. Promedio obtenido (x̄): {promedio:.6f}\n\n"
            f"Formula del Estadístico Calculado Z0:\n"
            f"   Z0 = | (x̄ - 0.5) * sqrt(N) | / sqrt(1/12)\n"
            f"Sustitución:\n"
            f"   Z0 = | ({promedio:.6f} - 0.5) * sqrt({n}) | / sqrt(0.083333)\n"
            f"   Z0 = | ({promedio - 0.5:.6f}) * {math.sqrt(n):.6f} | / {math.sqrt(1/12):.6f}\n"
            f"   Z0 = {abs(promedio - 0.5) * math.sqrt(n):.6f} / {math.sqrt(1/12):.6f}\n"
            f"   Z0 = {z_0:.6f}\n\n"
            f"Estadístico de Tablas Z_α/2:\n"
            f"   Z_α/2 = Z_({alfa:.4f}/2) = Z_{alfa_medios:.4f}\n"
            f"   Z_tablas = {z_tabla:.3f}\n\n"
            f"Evaluación de Hipótesis:\n"
            f"   ¿Z0 < Z_tablas?  =>  {z_0:.6f} {'<' if z_0 < z_tabla else '>='} {z_tabla:.3f}\n"
            f"   Resultado: {conclusion}\n"
        )
        self.txt_calculos.insert("1.0", desarrollo_completo)
        self.txt_calculos.configure(state="disabled")

        # Actualizar etiqueta inferior
        self.lbl_desarrollo.configure(
            text=f"Hipótesis Aceptada: Z0 = {z_0:.5f} < Z_tablas = {z_tabla:.3f}" if z_0 < z_tabla else f"Hipótesis Rechazada: Z0 = {z_0:.5f} >= Z_tablas = {z_tabla:.3f}",
            text_color=color_conclusion
        )

    def limpiar_resultados(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.txt_calculos.configure(state="normal")
        self.txt_calculos.delete("1.0", "end")
        self.txt_calculos.configure(state="disabled")

        self.tar_promedio.configure(text="—")
        self.tar_z0.configure(text="—")
        self.tar_ztabla.configure(text="—")
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
    app = PruebaPromedioApp()
    app.mainloop()