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


class GeneracionExponencialApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Generación Variable Exponencial | Modelado y Simulación")
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
        self.ent_media = self.crear_campo(panel_entrada, "Media estadística (λ):", "3")
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
            text="GENERACIÓN DE VARIABLES ALEATORIAS EXPONENCIALES",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ESTILOS.WHITE
        ).grid(row=0, column=0, sticky="w", pady=(10, 2))

        ctk.CTkLabel(
            panel_resultados,
            text="Fórmula de transformación inversa: x = -(1 / λ) * ln(R)  •  Donde R es uniforme (0,1).",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Tarjetas de Resultado Superior
        tarjetas = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        tarjetas.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        tarjetas.grid_columnconfigure(0, weight=1)
        tarjetas.grid_columnconfigure(1, weight=1)
        tarjetas.grid_columnconfigure(2, weight=1)

        self.tar_suma = self.crear_tarjeta(tarjetas, "Suma Total (Σ X)", 0)
        self.tar_promedio = self.crear_tarjeta(tarjetas, "Promedio (x̄)", 1)
        self.tar_n = self.crear_tarjeta(tarjetas, "Total Muestra (N)", 2)

        # Tabla de resultados
        marco_tabla = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        marco_tabla.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        marco_tabla.grid_rowconfigure(0, weight=1)
        marco_tabla.grid_columnconfigure(0, weight=1)

        columnas = ("i", "r", "x")
        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings")

        self.tabla.heading("i", text="i (Índice)")
        self.tabla.column("i", width=100, anchor="center")
        self.tabla.heading("r", text="R (Número Uniforme)")
        self.tabla.column("r", width=220, anchor="center")
        self.tabla.heading("x", text="X (Variable Exponencial)")
        self.tabla.column("x", width=250, anchor="center")

        barra_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=barra_y.set)

        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")

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
            media = float(self.ent_media.get())
            col = int(self.ent_col.get())
            reng = int(self.ent_reng.get())
        except ValueError:
            messagebox.showerror("Error de entrada", "Asegúrate de ingresar solo números válidos en los campos.")
            return

        if n <= 0 or media <= 0 or col <= 0 or reng <= 0:
            messagebox.showerror("Error de entrada", "Todos los parámetros deben ser mayores a cero.")
            return

        # 2. Cargar números
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

        # 3. Generar variables exponenciales y mostrarlas en la tabla
        resultados = []
        for i, r in enumerate(nums_r):
            try:
                x = -1.0 / media * math.log(r)
            except ValueError:
                x = 0.0
            resultados.append(x)
            self.tabla.insert("", "end", values=(i + 1, f"{r:.5f}", f"{x:.6f}"))

        # 4. Calcular suma y promedio
        total_suma = sum(resultados)
        total_promedio = total_suma / n

        # Actualizar Tarjetas
        self.tar_suma.configure(text=f"{total_suma:.5f}")
        self.tar_promedio.configure(text=f"{total_promedio:.6f}")
        self.tar_n.configure(text=str(n))

        # Actualizar veredicto inferior
        self.veredicto_frame.configure(fg_color="#0A3D2E", border_color=ESTILOS.GREEN, border_width=2)
        self.lbl_resumen.configure(
            text=f"Variables exponenciales generadas con éxito (media λ = {media}) | Suma total = {total_suma:.5f}",
            text_color=ESTILOS.GREEN
        )

    def limpiar_resultados(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        self.tar_suma.configure(text="—")
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
    app = GeneracionExponencialApp()
    app.mainloop()