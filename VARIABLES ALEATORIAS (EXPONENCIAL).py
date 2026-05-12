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
        print(f"Error: {e}")
        return None

def generar_exponencial():
    print("=== GENERACIÓN VARIABLE EXPONENCIAL ===")
    n = int(input("N (Cantidad): "))
    col = int(input("COL (1-10): "))
    reng = int(input("RENG: "))
    media = float(input("Media estadística (λ): ")) # Ejemplo: 3 minutos [cite: 70]

    nums_r = cargar_datos('DATOS/NUMEROS_ALEATORIOS.csv', n, col, reng)
    
    if nums_r:
        print(f"\n{'i':<5} | {'R (Uniforme)':<12} | {'X (Exponencial)':<12}")
        print("-" * 45)
        resultados = []
        for i, r in enumerate(nums_r):
            # Fórmula del PDF: x = -1/lambda * ln(R) donde 1/lambda es la media [cite: 64]
            x = -1/media * math.log(r)
            resultados.append(x)
            print(f"{i+1:<5} | {r:<12.5f} | {x:<12.6f}")
        
        print("-" * 45)
        print(f"TOTAL: {sum(resultados):.6f}")
        print(f"PROMEDIO: {sum(resultados)/len(resultados):.6f}")

if __name__ == "__main__":
    generar_exponencial()