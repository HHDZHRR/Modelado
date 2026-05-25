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
from tkinter import ttk, messagebox
import math
import os
import csv

ESTILOS.aplicar_tema()

DIRECTORIO_PROGRAMA = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV_PREDETERMINADA = os.path.join(
    DIRECTORIO_PROGRAMA,
    "DATOS",
    "NUMEROS_ALEATORIOS.csv"
)

# ==========================================
# DATOS Y DISTRIBUCIONES (Basados en el PDF)
# ==========================================
DEFAULT_RN_COL1 = [0.63325, 0.48355, 0.98977, 0.06533, 0.45128, 0.15486, 0.19241, 0.15997, 
                   0.67940, 0.90872, 0.58997, 0.68691, 0.73488, 0.98564, 0.89745]
DEFAULT_RN_COL2 = [0.83761, 0.14387, 0.51321, 0.72472, 0.05466, 0.84609, 0.29735, 0.59076, 
                   0.76355, 0.29549, 0.61958, 0.17267, 0.10061, 0.97623, 0.87953]

prob_initial_trucks = {0: 0.50, 1: 0.25, 2: 0.15, 3: 0.10}
prob_arrivals = {20: 0.02, 25: 0.08, 30: 0.12, 35: 0.25, 40: 0.20, 
                 45: 0.15, 50: 0.10, 55: 0.05, 60: 0.03}
prob_service = {
    3: {20: 0.05, 25: 0.10, 30: 0.20, 35: 0.25, 40: 0.12, 45: 0.10, 50: 0.08, 55: 0.06, 60: 0.04},
    4: {15: 0.05, 20: 0.15, 25: 0.20, 30: 0.20, 35: 0.15, 40: 0.12, 45: 0.08, 50: 0.04, 55: 0.01},
    5: {10: 0.10, 15: 0.18, 20: 0.22, 25: 0.18, 30: 0.10, 35: 0.08, 40: 0.06, 45: 0.05, 50: 0.03},
    6: {5: 0.12, 10: 0.15, 15: 0.26, 20: 0.15, 25: 0.12, 30: 0.08, 35: 0.06, 40: 0.04, 45: 0.02}
}

def get_value(rn, cdf_dict):
    cumulative = 0.0
    for value, prob in cdf_dict.items():
        cumulative += prob
        if rn <= cumulative + 1e-9:
            return value
    return list(cdf_dict.keys())[-1]

def parse_hhmm(time_str):
    try:
        parts = time_str.strip().split(":")
        hours = int(parts[0])
        mins = int(parts[1])
        if not (0 <= hours < 24 and 0 <= mins < 60):
            raise ValueError()
        return hours * 60 + mins
    except Exception:
        raise ValueError("La hora de inicio debe tener el formato HH:MM (de 00:00 a 23:59).")

def minutes_to_hhmm(minutes):
    total_min = int(round(minutes))
    hours = (total_min // 60) % 24
    mins = total_min % 60
    return f"{hours:02d}:{mins:02d}"

def simulate_warehouse_data(num_workers, rn_col1, rn_col2, start_time_minutes=660):
    break_start_limit = 240
    break_duration = 30
    shift_end = 510 
    
    rn_arr_idx = 1
    rn_srv_idx = 0
    
    if not rn_col1:
        return [], {"salario_normal": 0, "salario_extra": 0, "costo_espera": 0, "costo_almacen": 0, "costo_total": 0, "camiones": 0}
        
    rn_initial = rn_col1[0]
    initial_trucks = get_value(rn_initial, prob_initial_trucks)
    
    # Generar tiempos de llegada
    truck_arrivals = [0] * initial_trucks
    inter_arrivals = [0] * initial_trucks
    rn_arrivals = [""] * initial_trucks
    if initial_trucks > 0:
        rn_arrivals[0] = f"{rn_initial:.5f}"
        for k in range(1, initial_trucks):
            rn_arrivals[k] = "-"
            
    current_arrival_time = 0
    
    while rn_arr_idx < len(rn_col1):
        rn_arr = rn_col1[rn_arr_idx]
        inter_arrival = get_value(rn_arr, prob_arrivals)
        current_arrival_time += inter_arrival
        if current_arrival_time > shift_end:
            break
        truck_arrivals.append(current_arrival_time)
        inter_arrivals.append(inter_arrival)
        rn_arrivals.append(f"{rn_arr:.5f}")
        rn_arr_idx += 1

    server_available_time = 0
    break_taken = False
    total_wait_time = 0
    
    table_rows = []
    start_service_times = []
    
    for i, arrival_time in enumerate(truck_arrivals):
        # Lógica del descanso a las 3:00 a.m.
        if not break_taken and server_available_time <= break_start_limit and arrival_time >= break_start_limit:
            server_available_time = break_start_limit + break_duration
            break_taken = True
            
        idle_time = max(0, arrival_time - server_available_time) if i > 0 else 0
        start_service_time = max(arrival_time, server_available_time)
        
        if not break_taken and start_service_time >= break_start_limit:
            start_service_time = max(start_service_time, break_start_limit + break_duration)
            break_taken = True
            idle_time = 0 # El descanso no se cuenta como ocio
            
        wait_time = start_service_time - arrival_time
        total_wait_time += wait_time
        
        rn_srv = rn_col2[rn_srv_idx] if rn_srv_idx < len(rn_col2) else 0.5
        rn_srv_idx += 1
            
        service_time = get_value(rn_srv, prob_service[num_workers])
        end_service_time = start_service_time + service_time
        
        if not break_taken and start_service_time < break_start_limit and end_service_time >= break_start_limit:
            end_service_time += break_duration
            break_taken = True
            
        server_available_time = end_service_time
        
        # Calcular longitud de la cola al momento de la llegada
        if i < initial_trucks:
            queue_length = initial_trucks - i
        else:
            queue_length = sum(1 for prev_start in start_service_times if prev_start > arrival_time)
            if wait_time > 0:
                queue_length += 1
                
        start_service_times.append(start_service_time)
        
        # Guardar fila para la tabla:
        # 1. Numero Aleatorio
        # 2. Tiempo entre llegadas (min)
        # 3. Hora de tiempo de llegada (HH:MM)
        # 4. Hora de inicio del servicio (HH:MM)
        # 5. Numero Alearotio
        # 6. Tiempo de servicio (min)
        # 7. Hora de fin del servicio (HH:MM)
        # 8. Ocio del personal (sin "min")
        # 9. Tiempo de espera del camion (min)
        # 10. Longitud de la cola
        table_rows.append((
            rn_arrivals[i] if i < len(rn_arrivals) else "-",
            f"{inter_arrivals[i]} min" if i < len(inter_arrivals) else "- min",
            minutes_to_hhmm(start_time_minutes + arrival_time),
            minutes_to_hhmm(start_time_minutes + start_service_time),
            f"{rn_srv:.5f}",
            f"{service_time} min",
            minutes_to_hhmm(start_time_minutes + end_service_time),
            f"{idle_time}",
            f"{wait_time} min",
            f"{queue_length}"
        ))

    # Cálculo de costos
    extra_time_minutes = max(0, server_available_time - shift_end)
    extra_hours = extra_time_minutes / 60.0
    total_normal_salary = (8 * 25) * num_workers
    total_extra_salary = (37.50 * num_workers) * extra_hours
    cost_truck_wait = (total_wait_time / 60.0) * 100
    total_operation_minutes = max(shift_end, server_available_time)
    cost_warehouse_operation = (total_operation_minutes / 60.0) * 500
    
    total_cost = total_normal_salary + total_extra_salary + cost_truck_wait + cost_warehouse_operation
    
    stats = {
        "salario_normal": total_normal_salary,
        "salario_extra": total_extra_salary,
        "costo_espera": cost_truck_wait,
        "costo_almacen": cost_warehouse_operation,
        "costo_total": total_cost,
        "camiones": len(truck_arrivals)
    }
    
    return table_rows, stats

def cargar_dos_columnas(archivo, n, col1, col2, reng):
    """
    Carga n números para la columna 1 (llegadas) y n números para la columna 2 (servicio)
    empezando desde la fila 'reng' (bloques de 5 filas).
    """
    rn_col1 = []
    rn_col2 = []
    col1_idx = col1 - 1
    col2_idx = col2 - 1
    fila_inicio = (reng - 1) * 5

    if not os.path.exists(archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {archivo}")

    with open(archivo, 'r', encoding='utf-8-sig') as f:
        lector = csv.reader(f)
        filas = list(lector)

        for i in range(fila_inicio, min(fila_inicio + n, len(filas))):
            # Cargar col1
            if col1_idx < len(filas[i]):
                valor_texto = filas[i][col1_idx].strip()
                if valor_texto:
                    if "." in valor_texto:
                        v = float(valor_texto)
                    else:
                        v = float("0." + valor_texto)
                    rn_col1.append(v)
            # Cargar col2
            if col2_idx < len(filas[i]):
                valor_texto = filas[i][col2_idx].strip()
                if valor_texto:
                    if "." in valor_texto:
                        v = float(valor_texto)
                    else:
                        v = float("0." + valor_texto)
                    rn_col2.append(v)
    return rn_col1, rn_col2

class ColaSimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Colas | Modelado y Simulación")
        self.geometry("1200x750")
        self.configure(fg_color=ESTILOS.BG)
        self.minsize(1050, 600)
        
        self.ruta_csv = RUTA_CSV_PREDETERMINADA
        
        # Configurar rejilla
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

        # Origen de números
        ctk.CTkLabel(
            panel_entrada,
            text="Origen de números:",
            anchor="w",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=20, pady=(10, 2))

        self.origen_numeros = ctk.StringVar(value="Predeterminados")
        self.btn_origen = ctk.CTkSegmentedButton(
            panel_entrada,
            values=["Predeterminados", "CSV"],
            variable=self.origen_numeros,
            command=self.cambiar_origen_numeros
        )
        self.btn_origen.pack(fill="x", padx=20, pady=(0, 10))

        # Contenedor para controles de CSV
        self.contenedor_csv = ctk.CTkFrame(panel_entrada, fg_color="transparent")
        self.contenedor_csv.pack(fill="x", pady=0)

        self.frame_csv_cont = ctk.CTkFrame(self.contenedor_csv, fg_color="transparent")

        self.lbl_estado_csv = ctk.CTkLabel(
            self.frame_csv_cont,
            text="Verificando archivo...",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ESTILOS.MUTED,
            wraplength=240,
            justify="center"
        )
        self.lbl_estado_csv.pack(fill="x", padx=20, pady=(5, 5))

        self.btn_seleccionar_csv = ctk.CTkButton(
            self.frame_csv_cont,
            text="SELECCIONAR CSV",
            height=30,
            fg_color=ESTILOS.CARD,
            text_color=ESTILOS.WHITE,
            border_color=ESTILOS.BORDER,
            border_width=1,
            hover_color=ESTILOS.PANEL,
            command=self.seleccionar_csv
        )
        self.btn_seleccionar_csv.pack(fill="x", padx=20, pady=(0, 10))

        self.ent_n = self.crear_campo(self.frame_csv_cont, "N (Cantidad a cargar):", "15")
        self.ent_col1 = self.crear_campo(self.frame_csv_cont, "Col. Llegadas (1-10):", "1")
        self.ent_col2 = self.crear_campo(self.frame_csv_cont, "Col. Servicio (1-10):", "2")
        self.ent_reng = self.crear_campo(self.frame_csv_cont, "Bloque de Renglón (1+):", "1")

        # Hora de inicio del simulador
        self.ent_hora_inicio = self.crear_campo(panel_entrada, "Hora de inicio (HH:MM):", "11:00")

        # Tamaño del equipo (Segmented Button)
        ctk.CTkLabel(
            panel_entrada,
            text="Tamaño del equipo (Personas):",
            anchor="w",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=20, pady=(15, 2))

        self.equipo_var = ctk.StringVar(value="3")
        self.btn_equipo = ctk.CTkSegmentedButton(
            panel_entrada,
            values=["3", "4", "5", "6"],
            variable=self.equipo_var
        )
        self.btn_equipo.pack(fill="x", padx=20, pady=(0, 10))

        # Información de costos fijos
        ctk.CTkLabel(
            panel_entrada,
            text="Costos y Salarios:\n"
                 "• Salario Normal: $25/hr\n"
                 "• Salario Extra: $37.50/hr\n"
                 "• Costo Espera Camión: $100/hr\n"
                 "• Costo Almacén: $500/hr",
            justify="left",
            anchor="w",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=12)
        ).pack(fill="x", padx=20, pady=(15, 15))

        # Botones de Simulación
        ctk.CTkButton(
            panel_entrada,
            text="SIMULAR",
            height=45,
            fg_color=ESTILOS.GREEN,
            text_color=ESTILOS.BG,
            hover_color="#00B889",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.run_simulation
        ).pack(fill="x", padx=20, pady=(10, 10))

        ctk.CTkButton(
            panel_entrada,
            text="ÓPTIMO AUTOMÁTICO",
            height=35,
            fg_color=ESTILOS.CARD,
            text_color=ESTILOS.WHITE,
            border_color=ESTILOS.BORDER,
            border_width=1,
            hover_color=ESTILOS.PANEL,
            command=self.find_optimal
        ).pack(fill="x", padx=20, pady=(0, 20))

        # ── PANEL DERECHO (Resultados) ──
        panel_resultados = ctk.CTkFrame(self, fg_color=ESTILOS.BG)
        panel_resultados.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        panel_resultados.grid_columnconfigure(0, weight=1)
        panel_resultados.grid_rowconfigure(2, weight=1)

        # Encabezado
        ctk.CTkLabel(
            panel_resultados,
            text="SIMULADOR DE SISTEMAS DE COLAS",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=ESTILOS.WHITE
        ).grid(row=0, column=0, sticky="w", pady=(10, 2))

        ctk.CTkLabel(
            panel_resultados,
            text="Evaluación de costos y personal para la descarga del almacén central",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Tabla (Treeview)
        marco_tabla = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        marco_tabla.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        marco_tabla.grid_rowconfigure(0, weight=1)
        marco_tabla.grid_columnconfigure(0, weight=1)

        columns = (
            "rn_llegada",
            "tiempo_llegada",
            "hora_llegada",
            "hora_inicio",
            "rn_servicio",
            "tiempo_servicio",
            "hora_fin",
            "ocio",
            "espera",
            "cola"
        )
        self.tree = ttk.Treeview(marco_tabla, columns=columns, show="headings")

        headings = [
            "Número Aleatorio",
            "Tiempo entre llegadas",
            "Hora de tiempo de llegada",
            "Hora de inicio del servicio",
            "Número Aleatorio",
            "Tiempo de servicio",
            "Hora de fin del servicio",
            "Ocio del personal",
            "Tiempo de espera del camión",
            "Longitud de la cola"
        ]
        
        anchos = {
            "rn_llegada": 120,
            "tiempo_llegada": 150,
            "hora_llegada": 170,
            "hora_inicio": 180,
            "rn_servicio": 120,
            "tiempo_servicio": 130,
            "hora_fin": 170,
            "ocio": 130,
            "espera": 180,
            "cola": 130
        }

        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head)
            self.tree.column(col, anchor="center", width=anchos[col])

        barra_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tree.yview)
        barra_x = ttk.Scrollbar(marco_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")

        # PANEL INFERIOR (Tarjetas de resultados)
        marco_tarjetas = ctk.CTkFrame(panel_resultados, fg_color="transparent")
        marco_tarjetas.grid(row=3, column=0, sticky="ew", pady=(5, 5))
        for i in range(6):
            marco_tarjetas.grid_columnconfigure(i, weight=1)

        self.stat_labels = {}
        labels_txt = ["Camiones", "Salario Normal", "Salario Extra", "Costo Espera", "Costo Almacén", "COSTO TOTAL"]
        keys = ["camiones", "salario_normal", "salario_extra", "costo_espera", "costo_almacen", "costo_total"]

        for i, (label_text, key) in enumerate(zip(labels_txt, keys)):
            tarjeta = ctk.CTkFrame(marco_tarjetas, fg_color=ESTILOS.CARD, corner_radius=10, height=80, border_color=ESTILOS.BORDER, border_width=1)
            tarjeta.grid(row=0, column=i, sticky="ew", padx=3)
            tarjeta.grid_propagate(False)

            ctk.CTkLabel(
                tarjeta,
                text=label_text,
                text_color=ESTILOS.MUTED,
                font=ctk.CTkFont(size=11, weight="bold")
            ).place(relx=0.5, rely=0.3, anchor="center")

            val_lbl = ctk.CTkLabel(
                tarjeta,
                text="—",
                text_color=ESTILOS.WHITE,
                font=ctk.CTkFont(size=15, weight="bold")
            )
            val_lbl.place(relx=0.5, rely=0.7, anchor="center")
            self.stat_labels[key] = val_lbl

        # Tarjeta de Verificación/Veredicto al pie
        self.veredicto_frame = ctk.CTkFrame(panel_resultados, fg_color=ESTILOS.CARD, height=50, corner_radius=10, border_color=ESTILOS.BORDER, border_width=1)
        self.veredicto_frame.grid(row=4, column=0, sticky="ew", pady=(10, 5))
        self.veredicto_frame.grid_propagate(False)

        self.lbl_resumen = ctk.CTkLabel(
            self.veredicto_frame,
            text="Selecciona los parámetros y haz clic en SIMULAR.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=ESTILOS.MUTED
        )
        self.lbl_resumen.place(relx=0.5, rely=0.5, anchor="center")

    def cambiar_origen_numeros(self, origen):
        if origen == "CSV":
            self.frame_csv_cont.pack(fill="x", pady=5)
        else:
            self.frame_csv_cont.pack_forget()

    def seleccionar_csv(self):
        from tkinter import filedialog
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo CSV de números aleatorios",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.ruta_csv = archivo
            nombre_archivo = os.path.basename(archivo)
            self.lbl_estado_csv.configure(
                text=f"CSV: {nombre_archivo}",
                text_color=ESTILOS.GREEN
            )

    def crear_campo(self, padre, texto, valor):
        ctk.CTkLabel(
            padre,
            text=texto,
            anchor="w",
            text_color=ESTILOS.MUTED,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(fill="x", padx=20, pady=(5, 2))

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

    def obtener_numeros(self):
        if self.origen_numeros.get() == "Predeterminados":
            return DEFAULT_RN_COL1, DEFAULT_RN_COL2, "Valores Predeterminados"

        try:
            n = int(self.ent_n.get())
            col1 = int(self.ent_col1.get())
            col2 = int(self.ent_col2.get())
            reng = int(self.ent_reng.get())
        except ValueError:
            raise ValueError("Los parámetros de CSV deben ser números enteros válidos.")

        if n <= 0 or col1 <= 0 or col2 <= 0 or reng <= 0:
            raise ValueError("Todos los parámetros del CSV deben ser mayores a cero.")

        if not os.path.exists(self.ruta_csv):
            raise FileNotFoundError(f"Archivo CSV no detectado en: {self.ruta_csv}")

        rn1, rn2 = cargar_dos_columnas(self.ruta_csv, n, col1, col2, reng)
        
        if not rn1 or not rn2:
            raise ValueError("No se pudieron extraer suficientes números del CSV para las columnas indicadas.")

        if len(rn1) < n or len(rn2) < n:
            warnings_text = f"Se solicitaron {n} números pero solo se cargaron {min(len(rn1), len(rn2))} pares."
            messagebox.showwarning("Advertencia", warnings_text)

        min_len = min(len(rn1), len(rn2))
        return rn1[:min_len], rn2[:min_len], f"CSV ({os.path.basename(self.ruta_csv)})"

    def run_simulation(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            workers = int(self.equipo_var.get())
            rn_col1, rn_col2, origen = self.obtener_numeros()
            start_time_minutes = parse_hhmm(self.ent_hora_inicio.get())
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
            
        rows, stats = simulate_warehouse_data(workers, rn_col1, rn_col2, start_time_minutes)
        
        # Llenar tabla
        for row in rows:
            self.tree.insert("", tk.END, values=row)
            
        # Actualizar Tarjetas
        self.stat_labels["camiones"].configure(text=str(stats["camiones"]))
        self.stat_labels["salario_normal"].configure(text=f"${stats['salario_normal']:,.2f}")
        self.stat_labels["salario_extra"].configure(text=f"${stats['salario_extra']:,.2f}")
        self.stat_labels["costo_espera"].configure(text=f"${stats['costo_espera']:,.2f}")
        self.stat_labels["costo_almacen"].configure(text=f"${stats['costo_almacen']:,.2f}")
        self.stat_labels["costo_total"].configure(text=f"${stats['costo_total']:,.2f}", text_color=ESTILOS.GREEN)
        
        self.veredicto_frame.configure(fg_color="#0A3D2E", border_color=ESTILOS.GREEN, border_width=2)
        self.lbl_resumen.configure(
            text=f"Simulación ejecutada con éxito usando {origen}. Costo Total: ${stats['costo_total']:,.2f}",
            text_color=ESTILOS.GREEN
        )
        
    def find_optimal(self):
        try:
            rn_col1, rn_col2, origen = self.obtener_numeros()
            start_time_minutes = parse_hhmm(self.ent_hora_inicio.get())
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        best_cost = float('inf')
        best_workers = 0
        
        for w in [3, 4, 5, 6]:
            _, stats = simulate_warehouse_data(w, rn_col1, rn_col2, start_time_minutes)
            if stats["costo_total"] < best_cost:
                best_cost = stats["costo_total"]
                best_workers = w
                
        messagebox.showinfo("Resultado Óptimo", 
                            f"Al procesar todas las corridas con {origen}, el equipo óptimo es de:\n\n"
                            f"👉 {best_workers} Personas\n"
                            f"👉 Costo Total: ${best_cost:,.2f}")

if __name__ == "__main__":
    import tkinter as tk  # Importación local para compatibilidad interna de Tkinter en inicializaciones
    app = ColaSimulatorApp()
    app.mainloop()