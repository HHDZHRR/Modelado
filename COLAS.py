import tkinter as tk
from tkinter import ttk, messagebox
import math

# ==========================================
# DATOS Y DISTRIBUCIONES (Basados en el PDF)
# ==========================================
rn_col1 = [0.63325, 0.48355, 0.98977, 0.06533, 0.45128, 0.15486, 0.19241, 0.15997, 
           0.67940, 0.90872, 0.58997, 0.68691, 0.73488, 0.98564, 0.89745]
rn_col2 = [0.83761, 0.14387, 0.51321, 0.72472, 0.05466, 0.84609, 0.29735, 0.59076, 
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

def simulate_warehouse_data(num_workers):
    break_start_limit = 240
    break_duration = 30
    shift_end = 510 
    
    rn_arr_idx = 1
    rn_srv_idx = 0
    
    rn_initial = rn_col1[0]
    initial_trucks = get_value(rn_initial, prob_initial_trucks)
    
    # Generar tiempos de llegada
    truck_arrivals = [0] * initial_trucks
    current_arrival_time = 0
    
    while rn_arr_idx < len(rn_col1):
        rn_arr = rn_col1[rn_arr_idx]
        inter_arrival = get_value(rn_arr, prob_arrivals)
        current_arrival_time += inter_arrival
        if current_arrival_time > shift_end:
            break
        truck_arrivals.append(current_arrival_time)
        rn_arr_idx += 1

    server_available_time = 0
    break_taken = False
    total_wait_time = 0
    
    table_rows = []
    
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
        
        # Guardar fila para la tabla
        table_rows.append((
            i + 1, 
            f"{arrival_time} min", 
            f"{start_service_time} min", 
            f"{service_time} min", 
            f"{end_service_time} min", 
            f"{idle_time} min", 
            f"{wait_time} min"
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

class ColaSimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Colas | Modelado y Simulación")
        self.geometry("1200x700")
        self.configure(bg="#eaeff5")
        
        self.create_styles()
        self.create_layout()

    def create_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Estilo Treeview (Tabla)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#1e6091", foreground="white")
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=25)
        style.map("Treeview", background=[('selected', '#52a6ea')])
        
        # Estilo Botones
        style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), background="#3b82f6", foreground="white", padding=8)
        style.map("Primary.TButton", background=[('active', '#2563eb')])
        
        style.configure("Secondary.TButton", font=("Segoe UI", 11, "bold"), background="#6b7280", foreground="white", padding=8)
        style.map("Secondary.TButton", background=[('active', '#4b5563')])

    def create_layout(self):
        # Título principal
        header_frame = tk.Frame(self, bg="#eaeff5")
        header_frame.pack(fill=tk.X, pady=15)
        tk.Label(header_frame, text="SIMULADOR DEL PROBLEMA DE COLAS", font=("Segoe UI", 20, "bold"), bg="#eaeff5", fg="#1e293b").pack()
        tk.Label(header_frame, text="Evaluación de costos y personal para la descarga del almacén central", font=("Segoe UI", 12), bg="#eaeff5", fg="#64748b").pack()

        main_content = tk.Frame(self, bg="#eaeff5")
        main_content.pack(fill=tk.BOTH, expand=True, padx=20)

        # PANEL IZQUIERDO (Controles)
        left_panel = tk.Frame(main_content, bg="#d8e2ed", width=280)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)

        tk.Label(left_panel, text="Parámetros", font=("Segoe UI", 14, "bold"), bg="#d8e2ed").pack(pady=(15, 10))
        
        tk.Label(left_panel, text="Tamaño del equipo:", font=("Segoe UI", 10, "bold"), bg="#d8e2ed").pack(anchor="w", padx=20, pady=(10, 5))
        self.equipo_var = tk.IntVar(value=3)
        for i in [3, 4, 5, 6]:
            ttk.Radiobutton(left_panel, text=f"{i} Personas", variable=self.equipo_var, value=i).pack(anchor="w", padx=30, pady=2)
            
        tk.Label(left_panel, text="Salario Normal: $25/hr", font=("Segoe UI", 9), bg="#d8e2ed", fg="#475569").pack(anchor="w", padx=20, pady=(15, 2))
        tk.Label(left_panel, text="Salario Extra: $37.50/hr", font=("Segoe UI", 9), bg="#d8e2ed", fg="#475569").pack(anchor="w", padx=20, pady=2)
        tk.Label(left_panel, text="Costo Espera: $100/hr", font=("Segoe UI", 9), bg="#d8e2ed", fg="#475569").pack(anchor="w", padx=20, pady=2)
        tk.Label(left_panel, text="Costo Almacén: $500/hr", font=("Segoe UI", 9), bg="#d8e2ed", fg="#475569").pack(anchor="w", padx=20, pady=2)

        ttk.Button(left_panel, text="SIMULAR", style="Primary.TButton", command=self.run_simulation).pack(fill=tk.X, padx=20, pady=(30, 10))
        ttk.Button(left_panel, text="ÓPTIMO AUTOMÁTICO", style="Secondary.TButton", command=self.find_optimal).pack(fill=tk.X, padx=20)

        # PANEL DERECHO (Tabla)
        right_panel = tk.Frame(main_content, bg="white", bd=1, relief="solid")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(right_panel, text="Tabla de simulación", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=10)

        # Configuración del Treeview
        columns = ("camion", "llegada", "inicio", "servicio", "fin", "ocio", "espera")
        self.tree = ttk.Treeview(right_panel, columns=columns, show="headings")
        
        headings = ["No. Camión", "Llegada", "Inicio Servicio", "T. Servicio", "Fin Servicio", "Ocio Personal", "Espera Camión"]
        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head)
            self.tree.column(col, anchor="center", width=100)
            
        scrollbar = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # PANEL INFERIOR (Tarjetas de resultados)
        self.bottom_panel = tk.Frame(self, bg="#eaeff5")
        self.bottom_panel.pack(fill=tk.X, padx=20, pady=20)
        
        self.stat_vars = {
            "camiones": tk.StringVar(value="-"),
            "salario_normal": tk.StringVar(value="$-"),
            "salario_extra": tk.StringVar(value="$-"),
            "costo_espera": tk.StringVar(value="$-"),
            "costo_almacen": tk.StringVar(value="$-"),
            "costo_total": tk.StringVar(value="$-")
        }
        
        labels = ["Camiones", "Salario Normal", "Salario Extra", "Costo Espera", "Costo Almacén", "COSTO TOTAL"]
        keys = ["camiones", "salario_normal", "salario_extra", "costo_espera", "costo_almacen", "costo_total"]
        
        for i, (label_text, key) in enumerate(zip(labels, keys)):
            frame = tk.Frame(self.bottom_panel, bg="white", bd=1, relief="solid")
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if i==0 else 10, 0))
            
            tk.Label(frame, text=label_text, font=("Segoe UI", 10, "bold"), bg="white", fg="#475569").pack(pady=(10, 5))
            tk.Label(frame, textvariable=self.stat_vars[key], font=("Segoe UI", 14, "bold"), bg="white", fg="#0f172a").pack(pady=(0, 10))

    def run_simulation(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        workers = self.equipo_var.get()
        rows, stats = simulate_warehouse_data(workers)
        
        # Llenar tabla
        for row in rows:
            self.tree.insert("", tk.END, values=row)
            
        # Actualizar Tarjetas
        self.stat_vars["camiones"].set(str(stats["camiones"]))
        self.stat_vars["salario_normal"].set(f"${stats['salario_normal']:,.2f}")
        self.stat_vars["salario_extra"].set(f"${stats['salario_extra']:,.2f}")
        self.stat_vars["costo_espera"].set(f"${stats['costo_espera']:,.2f}")
        self.stat_vars["costo_almacen"].set(f"${stats['costo_almacen']:,.2f}")
        self.stat_vars["costo_total"].set(f"${stats['costo_total']:,.2f}")
        
    def find_optimal(self):
        best_cost = float('inf')
        best_workers = 0
        
        for w in [3, 4, 5, 6]:
            _, stats = simulate_warehouse_data(w)
            if stats["costo_total"] < best_cost:
                best_cost = stats["costo_total"]
                best_workers = w
                
        messagebox.showinfo("Resultado Óptimo", 
                            f"Al procesar todas las corridas, el equipo óptimo es de:\n\n"
                            f"👉 {best_workers} Personas\n"
                            f"👉 Costo Total: ${best_cost:,.2f}")

if __name__ == "__main__":
    app = ColaSimulatorApp()
    app.mainloop()