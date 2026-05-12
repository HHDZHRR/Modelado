import csv
import math

def cargar_datos(archivo, n, col, reng):
    numeros = []
    col_idx, fila_inicio = col - 1, (reng - 1) * 5
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            filas = list(csv.reader(f))
            for i in range(fila_inicio, min(fila_inicio + n, len(filas))):
                if col_idx < len(filas[i]):
                    numeros.append(float("0." + filas[i][col_idx].strip()))
        return numeros
    except Exception as e:
        return None

def generar_poisson():
    print("=== GENERACIÓN VARIABLE POISSON ===")
    n = int(input("N (Cantidad): "))
    col = int(input("COL (1-10): "))
    reng = int(input("RENG: "))
    lam = float(input("Media de Poisson (λ): "))

    # 1. Crear Tabla de Rangos (Probabilidad Acumulada) [cite: 88, 90]
    print("\n--- Tabla de Rangos (F(xi)) ---")
    tabla_rangos = []
    x_i, f_acum = 0, 0
    while f_acum < 0.99995: # Límite del PDF [cite: 89]
        prob = (math.exp(-lam) * (lam**x_i)) / math.factorial(x_i) # [cite: 84]
        f_acum += prob
        tabla_rangos.append((x_i, f_acum))
        print(f"X={x_i:<4} | f(xi)={prob:.6f} | F(xi)={f_acum:.6f}")
        x_i += 1

    # 2. Asignación de números del CSV
    nums_r = cargar_datos(r'DATOS\NUMEROS_ALEATORIOS.csv', n, col, reng)
    
    if nums_r:
        print(f"\n{'i':<5} | {'R (Uniforme)':<12} | {'X (Poisson)':<12}")
        print("-" * 40)
        resultados = []
        for i, r in enumerate(nums_r):
            valor_x = 0
            for val, acum in tabla_rangos:
                if r < acum:
                    valor_x = val
                    break
            resultados.append(valor_x)
            print(f"{i+1:<5} | {r:<12.5f} | {valor_x:<12}")
        
        print("-" * 40)
        print(f"DEMANDA TOTAL: {sum(resultados)}")

if __name__ == "__main__":
    generar_poisson()