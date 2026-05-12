import csv

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

def generar_uniforme_ab():
    print("=== GENERACIÓN VARIABLE UNIFORME (a, b) ===")
    n = int(input("N (Cantidad): "))
    col = int(input("COL (1-10): "))
    reng = int(input("RENG: "))
    a_val = float(input("Valor mínimo (a): "))
    b_val = float(input("Valor máximo (b): "))

    nums_r = cargar_datos(r'DATOS\NUMEROS_ALEATORIOS.csv', n, col, reng)
    
    if nums_r:
        print(f"\n{'i':<5} | {'R (Uniforme)':<12} | {'X (Uniforme a,b)':<15}")
        print("-" * 48)
        resultados = []
        for i, r in enumerate(nums_r):
            # Fórmula: x = a + (b - a) * R 
            x = a_val + (b_val - a_val) * r
            resultados.append(x)
            print(f"{i+1:<5} | {r:<12.5f} | {x:<15.5f}")
        
        print("-" * 48)
        print(f"TOTAL: {sum(resultados):.5f}")
        print(f"PROMEDIO: {sum(resultados)/len(resultados):.6f}")

if __name__ == "__main__":
    generar_uniforme_ab()