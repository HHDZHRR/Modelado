import csv
import os
import customtkinter as ctk
from tkinter import ttk, messagebox


# ============================================================
# SIMULADOR DE VOLADOS - MODELADO Y SIMULACIÓN DE SISTEMAS
# ============================================================
# Reglas:
# - Si el número rectangular es <= 0.5, se gana el volado.
# - Si es > 0.5, se pierde el volado.
# - Al ganar, la apuesta vuelve a la apuesta inicial.
# - Al perder, la apuesta se duplica.
# - Si la apuesta supera el saldo, solo se apuesta el saldo.
# - Una corrida termina únicamente en META o QUIEBRA.
# - Una corrida inconclusa puede mostrarse en tabla, pero NO se
#   cuenta en estadísticas ni probabilidades.
# ============================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Ruta automática: el CSV debe estar dentro de una carpeta DATOS
# ubicada junto al archivo Python del programa.
DIRECTORIO_PROGRAMA = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV_PREDETERMINADA = os.path.join(
    DIRECTORIO_PROGRAMA,
    "DATOS",
    "NUMEROS_ALEATORIOS.csv"
)


def formato_dinero(valor):
    """Convierte una cantidad a texto con símbolo de dinero."""
    if float(valor).is_integer():
        return f"${int(valor)}"
    return f"${valor:.2f}"


def ejecutar_simulacion(
    cantidad_inicial,
    apuesta_inicial,
    meta,
    numeros,
    corridas_objetivo=None
):
    """
    Ejecuta la simulación.

    corridas_objetivo:
      - None: modo automático; consume todos los números.
      - entero: modo manual; termina cuando completa esa cantidad
        de corridas concluidas o cuando se acaban los números.
    """
    filas = []
    corrida_actual = 1
    cantidad = cantidad_inicial
    apuesta = apuesta_inicial

    metas = 0
    quiebras = 0
    concluidas = 0
    numeros_usados = 0
    corrida_en_proceso = False

    for numero_rectangular in numeros:
        if corridas_objetivo is not None and concluidas >= corridas_objetivo:
            break

        numeros_usados += 1
        corrida_en_proceso = True

        cantidad_antes = cantidad
        apuesta_real = min(apuesta, cantidad)

        if numero_rectangular <= 0.5:
            gano = "Sí"
            cantidad += apuesta_real
            apuesta = apuesta_inicial
        else:
            gano = "No"
            cantidad -= apuesta_real
            apuesta = apuesta_real * 2

        resultado = "—"

        if cantidad >= meta:
            resultado = "Meta"
            metas += 1
            concluidas += 1
            corrida_en_proceso = False
        elif cantidad <= 0:
            resultado = "Quiebra"
            quiebras += 1
            concluidas += 1
            corrida_en_proceso = False

        filas.append(
            (
                corrida_actual,
                formato_dinero(cantidad_antes),
                formato_dinero(apuesta_real),
                f"{numero_rectangular:.5f}",
                gano,
                formato_dinero(cantidad),
                resultado
            )
        )

        if resultado in ("Meta", "Quiebra"):
            if corridas_objetivo is None or concluidas < corridas_objetivo:
                corrida_actual += 1
                cantidad = cantidad_inicial
                apuesta = apuesta_inicial

    p_meta = metas / concluidas if concluidas else 0
    p_quiebra = quiebras / concluidas if concluidas else 0

    return {
        "filas": filas,
        "concluidas": concluidas,
        "metas": metas,
        "quiebras": quiebras,
        "p_meta": p_meta,
        "p_quiebra": p_quiebra,
        "numeros_usados": numeros_usados,
        "inconclusa": corrida_en_proceso,
    }


class SimuladorVoladosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulador de Volados | Modelado y Simulación")
        self.geometry("1500x850")
        self.minsize(1220, 730)

        self.ruta_csv = RUTA_CSV_PREDETERMINADA
        self.total_columnas_csv = 0
        self.numeros_por_columna = {}

        self.configurar_estilo_tabla()
        self.crear_interfaz()
        self.cargar_csv(self.ruta_csv, mostrar_error=False)

    # ========================================================
    # INTERFAZ
    # ========================================================
    def configurar_estilo_tabla(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Treeview",
            font=("Arial", 11),
            rowheight=31,
            background="white",
            fieldbackground="white"
        )
        estilo.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold"),
            foreground="white",
            background="#155e94",
            padding=8
        )
        estilo.map("Treeview", background=[("selected", "#cde9ff")])

    def crear_interfaz(self):
        ctk.CTkLabel(
            self,
            text="SIMULADOR DEL PROBLEMA DE VOLADOS",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(pady=(16, 3))

        ctk.CTkLabel(
            self,
            text="Números rectangulares desde CSV o captura manual • Corridas automáticas o manuales",
            text_color="#555555",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 14))

        principal = ctk.CTkFrame(self, fg_color="transparent")
        principal.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        principal.grid_columnconfigure(1, weight=1)
        principal.grid_rowconfigure(0, weight=1)

        self.crear_panel_datos(principal)
        self.crear_panel_resultados(principal)

    def crear_panel_datos(self, padre):
        # Scroll para que jamás se pierda el formulario de columna
        panel = ctk.CTkScrollableFrame(padre, width=365)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        ctk.CTkLabel(
            panel,
            text="Datos del experimento",
            font=ctk.CTkFont(size=19, weight="bold")
        ).pack(pady=(8, 12))

        self.ent_cantidad = self.crear_campo(panel, "Cantidad inicial:", "50")
        self.ent_apuesta = self.crear_campo(panel, "Apuesta inicial:", "10")
        self.ent_meta = self.crear_campo(panel, "Meta:", "80")

        self.crear_separador(panel)

        # ----------------------------------------------------
        # Tipo de corridas
        # ----------------------------------------------------
        ctk.CTkLabel(
            panel,
            text="Modo de corridas:",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=12, pady=(5, 5))

        self.modo_corridas = ctk.StringVar(value="Automático")
        ctk.CTkSegmentedButton(
            panel,
            values=["Automático", "Manual"],
            variable=self.modo_corridas,
            command=self.cambiar_modo_corridas
        ).pack(fill="x", padx=12, pady=(0, 8))

        self.lbl_modo_automatico = ctk.CTkLabel(
            panel,
            text=(
                "Automático: usa todos los números disponibles.\n"
                "Las corridas inconclusas no se contabilizan."
            ),
            justify="left",
            anchor="w",
            text_color="#5d6670",
            font=ctk.CTkFont(size=11)
        )
        self.lbl_modo_automatico.pack(fill="x", padx=12, pady=(0, 5))

        self.frame_corridas_manual = ctk.CTkFrame(panel, fg_color="transparent")
        ctk.CTkLabel(
            self.frame_corridas_manual,
            text="Cantidad de corridas concluidas:",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", pady=(0, 4))
        self.ent_corridas = ctk.CTkEntry(self.frame_corridas_manual, height=34)
        self.ent_corridas.pack(fill="x")
        self.ent_corridas.insert(0, "5")
        ctk.CTkLabel(
            self.frame_corridas_manual,
            text="Se detiene al completar esa cantidad.",
            justify="left",
            anchor="w",
            text_color="#5d6670",
            font=ctk.CTkFont(size=11)
        ).pack(fill="x", pady=(4, 0))

        self.sep_despues_corridas = self.crear_separador(panel)

        # ----------------------------------------------------
        # Origen de números rectangulares
        # ----------------------------------------------------
        ctk.CTkLabel(
            panel,
            text="Origen de números rectangulares:",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=12, pady=(5, 5))

        self.origen_numeros = ctk.StringVar(value="CSV")
        ctk.CTkSegmentedButton(
            panel,
            values=["CSV", "Manual"],
            variable=self.origen_numeros,
            command=self.cambiar_origen_numeros
        ).pack(fill="x", padx=12, pady=(0, 10))

        # ----------------------------------------------------
        # FORMULARIO CSV / COLUMNA
        # ----------------------------------------------------
        self.frame_csv = ctk.CTkFrame(panel, fg_color="#eef4fa")
        self.frame_csv.pack(fill="x", padx=12, pady=(0, 10))

        ctk.CTkLabel(
            self.frame_csv,
            text="Archivo CSV de números",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=10, pady=(10, 6))

        self.lbl_archivo = ctk.CTkLabel(
            self.frame_csv,
            text="DATOS/NUMEROS_ALEATORIOS.csv",
            wraplength=290,
            justify="left",
            anchor="w",
            text_color="#155e94",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lbl_archivo.pack(fill="x", padx=10, pady=(0, 4))

        self.lbl_estado_archivo = ctk.CTkLabel(
            self.frame_csv,
            text="Buscando archivo...",
            wraplength=290,
            justify="left",
            anchor="w",
            text_color="#5d6670",
            font=ctk.CTkFont(size=11)
        )
        self.lbl_estado_archivo.pack(fill="x", padx=10, pady=(0, 7))

        ctk.CTkButton(
            self.frame_csv,
            text="Seleccionar CSV",
            command=self.seleccionar_csv,
            height=33,
            fg_color="#4b718c",
            hover_color="#36566d"
        ).pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            self.frame_csv,
            text="Columna del archivo CSV:",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=10, pady=(0, 5))

        self.columna_seleccionada = ctk.StringVar(value="1")
        self.menu_columna = ctk.CTkOptionMenu(
            self.frame_csv,
            values=["1"],
            variable=self.columna_seleccionada,
            command=self.actualizar_info_columna,
            height=35
        )
        self.menu_columna.pack(fill="x", padx=10)

        self.lbl_info_columna = ctk.CTkLabel(
            self.frame_csv,
            text="Carga el CSV para detectar sus columnas.",
            justify="left",
            anchor="w",
            text_color="#5d6670",
            font=ctk.CTkFont(size=11)
        )
        self.lbl_info_columna.pack(fill="x", padx=10, pady=(6, 10))

        # ----------------------------------------------------
        # Formulario manual de números
        # ----------------------------------------------------
        self.frame_numeros_manual = ctk.CTkFrame(panel, fg_color="#eef4fa")

        ctk.CTkLabel(
            self.frame_numeros_manual,
            text="Captura de números rectangulares",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=10, pady=(10, 6))

        self.txt_numeros = ctk.CTkTextbox(
            self.frame_numeros_manual,
            height=190,
            font=ctk.CTkFont(size=12)
        )
        self.txt_numeros.pack(fill="x", padx=10)

        self.txt_numeros.insert(
            "1.0",
            "0.63325\n0.48355\n0.98977\n0.06533\n0.45128\n"
            "0.15486\n0.19241\n0.15997\n0.67940\n0.90872\n"
            "0.58997\n0.68691\n0.73488\n0.98564\n0.89745\n"
            "0.83761\n0.14387\n0.51321\n0.72472\n0.05466"
        )

        ctk.CTkLabel(
            self.frame_numeros_manual,
            text="Acepta 0.63325 o 63325, separados por espacios o líneas.",
            wraplength=300,
            justify="left",
            anchor="w",
            text_color="#5d6670",
            font=ctk.CTkFont(size=11)
        ).pack(fill="x", padx=10, pady=(5, 10))

        self.btn_simular = ctk.CTkButton(
            panel,
            text="SIMULAR",
            height=43,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.simular
        )
        self.btn_simular.pack(fill="x", padx=12, pady=(9, 7))

        ctk.CTkButton(
            panel,
            text="LIMPIAR RESULTADOS",
            height=38,
            fg_color="#667085",
            hover_color="#525d70",
            command=self.limpiar_resultados
        ).pack(fill="x", padx=12, pady=(0, 12))

    def crear_separador(self, padre):
        separador = ctk.CTkFrame(padre, height=1, fg_color="#d4dce4")
        separador.pack(fill="x", padx=12, pady=12)
        return separador

    def crear_campo(self, padre, texto, valor):
        ctk.CTkLabel(
            padre,
            text=texto,
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=12, pady=(5, 4))

        entrada = ctk.CTkEntry(padre, height=34)
        entrada.pack(fill="x", padx=12)
        entrada.insert(0, valor)
        return entrada

    def crear_panel_resultados(self, padre):
        panel = ctk.CTkFrame(padre)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            panel,
            text="Tabla de simulación",
            font=ctk.CTkFont(size=19, weight="bold")
        ).grid(row=0, column=0, pady=(15, 10))

        marco_tabla = ctk.CTkFrame(panel, fg_color="transparent")
        marco_tabla.grid(row=1, column=0, sticky="nsew", padx=14)
        marco_tabla.grid_rowconfigure(0, weight=1)
        marco_tabla.grid_columnconfigure(0, weight=1)

        columnas = (
            "corrida", "antes", "apuesta", "aleatorio",
            "gano", "despues", "resultado"
        )

        self.tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings")
        encabezados = {
            "corrida": "Número de\ncorrida",
            "antes": "Cantidad antes\ndel volado",
            "apuesta": "Apuesta",
            "aleatorio": "Número\nrectangular",
            "gano": "¿Se ganó el\nvolado?",
            "despues": "Cantidad después\ndel volado",
            "resultado": "Resultado"
        }
        anchos = {
            "corrida": 100, "antes": 145, "apuesta": 105,
            "aleatorio": 135, "gano": 125, "despues": 155,
            "resultado": 125
        }

        for columna in columnas:
            self.tabla.heading(columna, text=encabezados[columna])
            self.tabla.column(columna, width=anchos[columna], anchor="center")

        barra_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        barra_x = ttk.Scrollbar(marco_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(
            yscrollcommand=barra_y.set,
            xscrollcommand=barra_x.set
        )

        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")

        tarjetas = ctk.CTkFrame(panel)
        tarjetas.grid(row=2, column=0, sticky="ew", padx=14, pady=(13, 8))
        for i in range(5):
            tarjetas.grid_columnconfigure(i, weight=1)

        self.tar_concluidas = self.crear_tarjeta(tarjetas, "Concluidas", 0)
        self.tar_meta = self.crear_tarjeta(tarjetas, "Llegó a Meta", 1)
        self.tar_quiebra = self.crear_tarjeta(tarjetas, "Quiebra", 2)
        self.tar_p_meta = self.crear_tarjeta(tarjetas, "P(Meta)", 3)
        self.tar_p_quiebra = self.crear_tarjeta(tarjetas, "P(Quiebra)", 4)

        self.lbl_resumen = ctk.CTkLabel(
            panel,
            text="Configura el experimento y presiona SIMULAR.",
            font=ctk.CTkFont(size=13, weight="bold"),
            justify="left",
            anchor="w"
        )
        self.lbl_resumen.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 14))

    def crear_tarjeta(self, padre, titulo, columna):
        tarjeta = ctk.CTkFrame(padre, fg_color="#eef4fa")
        tarjeta.grid(row=0, column=columna, sticky="ew", padx=5, pady=6)

        ctk.CTkLabel(
            tarjeta,
            text=titulo,
            text_color="#425466",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(8, 2))

        valor = ctk.CTkLabel(
            tarjeta,
            text="—",
            text_color="#0e5689",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        valor.pack(pady=(0, 8))
        return valor

    # ========================================================
    # MODOS DEL FORMULARIO
    # ========================================================
    def cambiar_modo_corridas(self, modo):
        if modo == "Manual":
            self.lbl_modo_automatico.pack_forget()
            self.frame_corridas_manual.pack(
                fill="x", padx=12, pady=(0, 5),
                before=self.sep_despues_corridas
            )
        else:
            self.frame_corridas_manual.pack_forget()
            self.lbl_modo_automatico.pack(
                fill="x", padx=12, pady=(0, 5),
                before=self.sep_despues_corridas
            )

    def cambiar_origen_numeros(self, origen):
        if origen == "CSV":
            self.frame_numeros_manual.pack_forget()
            self.frame_csv.pack(
                fill="x", padx=12, pady=(0, 10),
                before=self.btn_simular
            )
        else:
            self.frame_csv.pack_forget()
            self.frame_numeros_manual.pack(
                fill="x", padx=12, pady=(0, 10),
                before=self.btn_simular
            )

    # ========================================================
    # ARCHIVO CSV Y LECTURA DE NÚMEROS
    # ========================================================
    def cargar_csv(self, ruta=None, mostrar_error=True):
        """Carga el CSV desde la ruta indicada o la predeterminada."""
        if ruta is None:
            ruta = RUTA_CSV_PREDETERMINADA
        self.ruta_csv = ruta

        if not os.path.exists(self.ruta_csv):
            self.numeros_por_columna = {}
            self.total_columnas_csv = 0
            self.menu_columna.configure(values=["1"])
            self.columna_seleccionada.set("1")
            self.lbl_estado_archivo.configure(
                text="No encontrado. Colócalo en DATOS o selecciona otro.",
                text_color="#b45309"
            )
            self.lbl_info_columna.configure(
                text="No se han detectado columnas."
            )
            if mostrar_error:
                messagebox.showerror(
                    "Archivo CSV no encontrado",
                    f"No se encontró el archivo:\n\n{self.ruta_csv}"
                )
            return False

        try:
            columnas = self.analizar_csv(self.ruta_csv)
        except (ValueError, OSError) as error:
            self.numeros_por_columna = {}
            self.total_columnas_csv = 0
            self.lbl_estado_archivo.configure(
                text="Archivo encontrado, pero no se pudo leer.",
                text_color="#b42318"
            )
            if mostrar_error:
                messagebox.showerror("Error al leer CSV", str(error))
            return False

        self.numeros_por_columna = columnas
        self.total_columnas_csv = len(columnas)
        opciones = [str(numero) for numero in columnas.keys()]
        self.menu_columna.configure(values=opciones)

        seleccion = self.columna_seleccionada.get()
        if seleccion not in opciones:
            seleccion = opciones[0]
            self.columna_seleccionada.set(seleccion)

        self.lbl_estado_archivo.configure(
            text="Archivo cargado correctamente.",
            text_color="#146c43"
        )
        self.actualizar_info_columna(seleccion)
        return True

    def seleccionar_csv(self):
        from tkinter import filedialog
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de números aleatorios",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.lbl_archivo.configure(text=os.path.basename(archivo))
            self.cargar_csv(archivo, mostrar_error=True)

    def analizar_csv(self, ruta):
        filas = []
        with open(ruta, "r", newline="", encoding="utf-8-sig") as archivo:
            for fila in csv.reader(archivo):
                filas.append(fila)

        if not filas:
            raise ValueError("El archivo CSV está vacío.")

        max_columnas = max(len(fila) for fila in filas)
        columnas = {}

        for indice in range(max_columnas):
            numeros = []
            for fila in filas:
                if indice < len(fila) and fila[indice].strip() != "":
                    numeros.append(self.convertir_rectangular(fila[indice]))
            if numeros:
                columnas[indice + 1] = numeros

        if not columnas:
            raise ValueError("No se encontraron números válidos en el CSV.")

        return columnas

    def actualizar_info_columna(self, seleccion):
        if not self.numeros_por_columna:
            return

        columna = int(seleccion)
        cantidad = len(self.numeros_por_columna[columna])
        self.lbl_info_columna.configure(
            text=(
                f"Columnas detectadas: {self.total_columnas_csv}  |  "
                f"Números en columna {columna}: {cantidad}"
            )
        )

    @staticmethod
    def convertir_rectangular(valor):
        texto = str(valor).strip()

        if texto == "":
            raise ValueError("Se encontró un valor vacío.")

        # Acepta tanto 0.63325 como 63325/03991.
        if "." in texto:
            numero = float(texto)
        else:
            if not texto.isdigit():
                raise ValueError(f"El valor '{texto}' no es un número rectangular válido.")
            numero = int(texto) / (10 ** len(texto))

        if numero < 0 or numero > 1:
            raise ValueError(f"El valor '{texto}' debe representar un número entre 0 y 1.")

        return numero

    def obtener_numeros(self):
        if self.origen_numeros.get() == "CSV":
            if not self.cargar_csv(self.ruta_csv, mostrar_error=False):
                raise ValueError(
                    f"No se pudo cargar el archivo CSV: {self.ruta_csv}"
                )
            columna = int(self.columna_seleccionada.get())
            return self.numeros_por_columna[columna], f"CSV, columna {columna}"

        texto = self.txt_numeros.get("1.0", "end").strip()
        if not texto:
            raise ValueError("Escribe al menos un número rectangular.")

        elementos = texto.replace(",", " ").replace(";", " ").split()
        numeros = [self.convertir_rectangular(elemento) for elemento in elementos]
        return numeros, "Captura manual"

    # ========================================================
    # EJECUCIÓN Y ESTADÍSTICAS
    # ========================================================
    def obtener_parametros(self):
        try:
            inicial = float(self.ent_cantidad.get())
            apuesta = float(self.ent_apuesta.get())
            meta = float(self.ent_meta.get())
        except ValueError:
            raise ValueError("Cantidad inicial, apuesta inicial y meta deben ser números.")

        if inicial <= 0:
            raise ValueError("La cantidad inicial debe ser mayor a cero.")
        if apuesta <= 0:
            raise ValueError("La apuesta inicial debe ser mayor a cero.")
        if meta <= inicial:
            raise ValueError("La meta debe ser mayor que la cantidad inicial.")
        if apuesta > inicial:
            raise ValueError("La apuesta inicial no puede superar la cantidad inicial.")

        objetivo = None
        if self.modo_corridas.get() == "Manual":
            try:
                objetivo = int(self.ent_corridas.get())
            except ValueError:
                raise ValueError("La cantidad de corridas debe ser un número entero.")
            if objetivo <= 0:
                raise ValueError("La cantidad de corridas debe ser mayor a cero.")

        return inicial, apuesta, meta, objetivo

    def simular(self):
        self.limpiar_resultados()

        try:
            inicial, apuesta, meta, objetivo = self.obtener_parametros()
            numeros, origen = self.obtener_numeros()
        except (ValueError, OSError) as error:
            messagebox.showerror("Datos incorrectos", str(error))
            return

        resultado = ejecutar_simulacion(
            inicial, apuesta, meta, numeros, objetivo
        )

        for fila in resultado["filas"]:
            self.tabla.insert("", "end", values=fila)

        concluidas = resultado["concluidas"]
        metas = resultado["metas"]
        quiebras = resultado["quiebras"]
        p_meta = resultado["p_meta"]
        p_quiebra = resultado["p_quiebra"]

        self.tar_concluidas.configure(text=str(concluidas))
        self.tar_meta.configure(text=str(metas))
        self.tar_quiebra.configure(text=str(quiebras))
        self.tar_p_meta.configure(text=f"{p_meta:.2%}")
        self.tar_p_quiebra.configure(text=f"{p_quiebra:.2%}")

        if self.modo_corridas.get() == "Automático":
            estado = "Modo automático: se consumieron todos los números disponibles."
            color = "#17496b"
        elif concluidas >= objetivo:
            estado = f"Modo manual: se completaron las {objetivo} corridas solicitadas."
            color = "#146c43"
        else:
            faltan = objetivo - concluidas
            estado = (
                f"Modo manual: no alcanzaron los números; "
                f"faltaron {faltan} corrida(s) concluida(s)."
            )
            color = "#b45309"

        inconclusa = (
            "Sí; se muestra en tabla pero no cuenta."
            if resultado["inconclusa"]
            else "No."
        )

        if concluidas:
            formulas = (
                f"P(Meta) = {metas}/{concluidas} = {p_meta:.4f} = {p_meta:.2%}   |   "
                f"P(Quiebra) = {quiebras}/{concluidas} = {p_quiebra:.4f} = {p_quiebra:.2%}"
            )
        else:
            formulas = "No existen corridas concluidas para calcular probabilidades."

        self.lbl_resumen.configure(
            text=(
                f"{estado}\n"
                f"Origen: {origen}  |  Números utilizados: {resultado['numeros_usados']}  |  "
                f"Corrida inconclusa: {inconclusa}\n"
                f"{formulas}"
            ),
            text_color=color
        )

    def limpiar_resultados(self):
        for elemento in self.tabla.get_children():
            self.tabla.delete(elemento)

        self.tar_concluidas.configure(text="—")
        self.tar_meta.configure(text="—")
        self.tar_quiebra.configure(text="—")
        self.tar_p_meta.configure(text="—")
        self.tar_p_quiebra.configure(text="—")

        self.lbl_resumen.configure(
            text="Configura el experimento y presiona SIMULAR.",
            text_color=("black", "white")
        )


if __name__ == "__main__":
    app = SimuladorVoladosApp()
    app.mainloop()
