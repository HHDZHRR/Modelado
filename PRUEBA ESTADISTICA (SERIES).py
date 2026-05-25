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


class PruebaSeriesApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Prueba de Series | Modelado y Simulación")
        self.geometry("1200x780")
        self.configure(fg_color=ESTILOS.BG)
        self.minsize(1000, 600)

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
        self.ent_n = self.crear_campo(panel_entrada, "N (Cantidad de números):", "40")
        self.ent_alpha = self.crear_campo(panel_entrada, "α (% de significancia, ej. 5):", "5")
        self.ent_k = self.crear_campo(panel_entrada, "Subintervalos por eje (n):", "3")
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
            text="PRUEBA ESTADÍSTICA DE SERIES (DISTRIBUCIÓN BIDIMENSIONAL)",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ESTILOS.WHITE
        ).grid(row=0, column=0, sticky="w", pady=(10, 2))

        ctk.CTkLabel(
            panel_resultados,
            text="Agrupa los números en parejas y evalúa su uniformidad y correlación espacial en una cuadrícula.",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Tarjetas de Resultado Superior
        tarjetas = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        tarjetas.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        tarjetas.grid_columnconfigure(0, weight=1)
        tarjetas.grid_columnconfigure(1, weight=1)
        tarjetas.grid_columnconfigure(2, weight=2)

        self.tar_x0 = self.crear_tarjeta(tarjetas, "Estadístico X0² Calculado", 0)
        self.tar_xtabla = self.crear_tarjeta(tarjetas, "Estadístico X² Tabla", 1)
        self.tar_conclusion = self.crear_tarjeta(tarjetas, "Conclusión Final", 2)

        # Tabview para ver Parejas, Matriz y Cálculos
        self.tabview = ctk.CTkTabview(panel_resultados, fg_color=ESTILOS.PANEL, segmented_button_selected_color=ESTILOS.GREEN)
        self.tabview.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        tab_parejas = self.tabview.add("Parejas y Matriz FOi")
        tab_calculos = self.tabview.add("Desarrollo de Parejas")
        tab_numeros = self.tabview.add("Números Extraídos")

        # Configurar Tab 1 (Parejas formadas + Matriz FOi visual)
        tab_parejas.grid_columnconfigure(0, weight=1)
        tab_parejas.grid_columnconfigure(1, weight=1)
        tab_parejas.grid_rowconfigure(0, weight=1)

        # Izquierda del tab 1: Parejas formadas
        marco_tabla = ctk.CTkFrame(tab_parejas, fg_color="transparent")
        marco_tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        marco_tabla.grid_rowconfigure(0, weight=1)
        marco_tabla.grid_columnconfigure(0, weight=1)

        columnas = ("pareja", "x", "y")
        self.tabla_parejas = ttk.Treeview(marco_tabla, columns=columnas, show="headings")
        self.tabla_parejas.heading("pareja", text="i")
        self.tabla_parejas.column("pareja", width=60, anchor="center")
        self.tabla_parejas.heading("x", text="X (xi)")
        self.tabla_parejas.column("x", width=110, anchor="center")
        self.tabla_parejas.heading("y", text="Y (xi+1)")
        self.tabla_parejas.column("y", width=110, anchor="center")

        barra_y_p = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla_parejas.yview)
        self.tabla_parejas.configure(yscrollcommand=barra_y_p.set)
        self.tabla_parejas.grid(row=0, column=0, sticky="nsew")
        barra_y_p.grid(row=0, column=1, sticky="ns")

        # Derecha del tab 1: Matriz FOi
        self.txt_matriz = ctk.CTkTextbox(
            tab_parejas,
            fg_color=ESTILOS.CARD,
            text_color=ESTILOS.WHITE,
            border_color=ESTILOS.BORDER,
            border_width=1,
            font=ctk.CTkFont(family="Courier", size=13)
        )
        self.txt_matriz.grid(row=0, column=1, sticky="nsew")

        # Configurar Tab 2 (Desarrollo FOi - FEi)
        tab_calculos.grid_columnconfigure(0, weight=1)
        tab_calculos.grid_rowconfigure(0, weight=1)
        self.txt_calculos = ctk.CTkTextbox(
            tab_calculos,
            fg_color=ESTILOS.CARD,
            text_color=ESTILOS.WHITE,
            border_color=ESTILOS.BORDER,
            border_width=1,
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.txt_calculos.grid(row=0, column=0, sticky="nsew")

        # Configurar Tab 3 (Números Extraídos)
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

        # Desarrollo del estadístico abajo (Tarjeta de Verificación)
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
            n_sub = int(self.ent_k.get())
            col = int(self.ent_col.get())
            reng = int(self.ent_reng.get())
        except ValueError:
            messagebox.showerror("Error de entrada", "Asegúrate de ingresar solo números válidos en los campos.")
            return

        if n <= 1 or alpha_pct <= 0 or alpha_pct >= 100 or n_sub <= 0 or col <= 0 or reng <= 0:
            messagebox.showerror("Error de entrada", "Los parámetros N (mínimo 2), subintervalos, columna y renglón deben ser mayores a cero. α debe estar entre 0 y 100.")
            return

        # 2. Cargar números
        try:
            numeros = cargar_numeros(self.ruta_csv, n, col, reng)
        except Exception as e:
            messagebox.showerror("Error al cargar archivo", f"No se pudo leer el archivo:\n{str(e)}")
            return

        if not numeros or len(numeros) < 2:
            messagebox.showerror("Error", "Se necesitan al menos 2 números para formar parejas en la prueba de series.")
            return

        if len(numeros) < n:
            messagebox.showwarning("Advertencia", f"Solo se pudieron cargar {len(numeros)} números en lugar de los {n} solicitados.")
            n = len(numeros)

        # 3. Mostrar números extraídos
        self.txt_numeros.configure(state="normal")
        self.txt_numeros.delete("1.0", "end")
        for i in range(0, len(numeros), 5):
            grupo = numeros[i:i+5]
            grupo_str = "   ".join([f"{num:.5f}" for num in grupo])
            self.txt_numeros.insert("end", f"[{i+1:02d}-{min(i+5, len(numeros)):02d}]:  {grupo_str}\n")
        self.txt_numeros.configure(state="disabled")

        # 4. Formar parejas e insertar en tabla
        parejas = []
        for i in range(n - 1):
            p = (numeros[i], numeros[i+1])
            parejas.append(p)
            self.tabla_parejas.insert("", "end", values=(i + 1, f"{p[0]:.5f}", f"{p[1]:.5f}"))

        # 5. Frecuencia Esperada FE = (N - 1) / n^2
        fe = (n - 1) / (n_sub ** 2)

        # Inicializar matriz de ceros
        fo = [[0] * n_sub for _ in range(n_sub)]

        # Ubicar parejas en la cuadrícula
        for x, y in parejas:
            c = int(x * n_sub)
            f = int(y * n_sub)
            if c == n_sub:
                c -= 1
            if f == n_sub:
                f -= 1
            fo[f][c] += 1

        # Renderizar la matriz en el textbox
        self.txt_matriz.configure(state="normal")
        self.txt_matriz.delete("1.0", "end")
        self.txt_matriz.insert("end", f"MATRIZ DE FRECUENCIAS (FOi):\n")
        self.txt_matriz.insert("end", f"Frecuencia Esperada (FE): {fe:.4f}\n")
        self.txt_matriz.insert("end", f"N-1 Parejas = {n - 1}\n\n")

        self.txt_matriz.insert("end", "   ┌" + "───" * n_sub + "─┐\n")
        for f_idx in reversed(range(n_sub)):
            fila = fo[f_idx]
            fila_str = " ".join([f"{val:2d}" for val in fila])
            self.txt_matriz.insert("end", f"{f_idx:2d} │ {fila_str} │\n")
        self.txt_matriz.insert("end", "   └" + "───" * n_sub + "─┘\n")
        col_cabecera = "   " + "  ".join([str(i) for i in range(n_sub)])
        self.txt_matriz.insert("end", f"{col_cabecera}\n")
        self.txt_matriz.configure(state="disabled")

        # 6. Estadístico X0^2
        suma_cuadrados = 0
        self.txt_calculos.configure(state="normal")
        self.txt_calculos.delete("1.0", "end")
        self.txt_calculos.insert("end", f"=== DETALLE DE CÁLCULO DE DIFERENCIAS ===\n\n")

        for f_idx in range(n_sub):
            for c_idx in range(n_sub):
                diferencia_cuad = (fo[f_idx][c_idx] - fe) ** 2
                suma_cuadrados += diferencia_cuad
                self.txt_calculos.insert(
                    "end",
                    f"Celda ({f_idx},{c_idx}): FO = {fo[f_idx][c_idx]:2d} | FE = {fe:.4f} | "
                    f"(FO-FE)² = {diferencia_cuad:.6f}\n"
                )

        x0_cuadrado = (n_sub ** 2 / (n - 1)) * suma_cuadrados

        self.txt_calculos.insert("end", f"\nSuma total de diferencias cuadradas: {suma_cuadrados:.6f}\n")
        self.txt_calculos.insert(
            "end",
            f"Fórmula: X0² = (n² / (N-1)) * Σ(FOi - FEi)²\n"
            f"X0² = ({n_sub}² / {n-1}) * {suma_cuadrados:.6f}\n"
            f"X0² = {x0_cuadrado:.6f}\n"
        )
        self.txt_calculos.configure(state="disabled")

        # 7. Estadístico de tablas
        alfa = alpha_pct / 100.0
        grados_libertad = (n_sub ** 2) - 1
        x_tabla = stats.chi2.ppf(1 - alfa, grados_libertad)

        # Aceptación
        if x0_cuadrado < x_tabla:
            conclusion = "Uniformes (Aceptados) ✅"
            color_conclusion = ESTILOS.GREEN
            self.veredicto_frame.configure(fg_color="#0A3D2E", border_color=ESTILOS.GREEN, border_width=2)
        else:
            conclusion = "No Uniformes (Rechazados) ❌"
            color_conclusion = ESTILOS.RED
            self.veredicto_frame.configure(fg_color="#3D0A0A", border_color=ESTILOS.RED, border_width=2)

        # Actualizar Tarjetas
        self.tar_x0.configure(text=f"{x0_cuadrado:.5f}")
        self.tar_xtabla.configure(text=f"{x_tabla:.5f}")
        self.tar_conclusion.configure(text=conclusion, text_color=color_conclusion)

        # Actualizar desarrollo inferior
        self.lbl_desarrollo.configure(
            text=f"Hipótesis Aceptada: X0² = {x0_cuadrado:.5f} < X²_tablas = {x_tabla:.5f}" if x0_cuadrado < x_tabla else f"Hipótesis Rechazada: X0² = {x0_cuadrado:.5f} >= X²_tablas = {x_tabla:.5f}",
            text_color=color_conclusion
        )

    def limpiar_resultados(self):
        for item in self.tabla_parejas.get_children():
            self.tabla_parejas.delete(item)
        self.txt_matriz.configure(state="normal")
        self.txt_matriz.delete("1.0", "end")
        self.txt_matriz.configure(state="disabled")
        self.txt_calculos.configure(state="normal")
        self.txt_calculos.delete("1.0", "end")
        self.txt_calculos.configure(state="disabled")
        self.txt_numeros.configure(state="normal")
        self.txt_numeros.delete("1.0", "end")
        self.txt_numeros.configure(state="disabled")

        self.tar_x0.configure(text="—")
        self.tar_xtabla.configure(text="—")
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
    app = PruebaSeriesApp()
    app.mainloop()