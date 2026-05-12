import csv
import scipy.stats as stats

def cargar_numeros(archivo, n, a, col, reng):
    """
    Extrae números de un archivo CSV basado en bloques de 5 filas.
    """
    numeros = []
    col_idx = col - 1 
    fila_inicio = (reng - 1) * 5 
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            lector = csv.reader(f)
            filas = list(lector)
            
            # Extraer N números desde el renglón solicitado
            for i in range(fila_inicio, min(fila_inicio + n, len(filas))):
                if col_idx < len(filas[i]):
                    valor_texto = filas[i][col_idx].strip()
                    # Convertir texto a decimal 0.XXXXX
                    valor_decimal = float("0." + valor_texto)
                    numeros.append(valor_decimal)
                    
        print(f"\n======================================")
        print(f" DATOS EXTRAÍDOS PARA K-S")
        print(f"======================================")
        print(f"Se extrajeron: {len(numeros)} números")
        print(f"Lista original: {numeros}")
        
        return numeros, a
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta '{archivo}'.")
        return None, None

def prueba_kolmogorov(numeros, a):
    """
    Aplica la Prueba de Kolmogorov-Smirnov según el documento PDF.
    """
    N = len(numeros)
    if N == 0: return

    print(f"\n======================================")
    print(f" EJECUTANDO PRUEBA KOLMOGOROV-SMIRNOV")
    print(f"======================================")

    # Paso 2: Ordenar en forma ascendente
    numeros_ordenados = sorted(numeros)
    
    # Paso 3 y 4: Calcular distancias Dn = max |(i/N) - xi|
    print(f"{'i':<4} | {'xi (Ordenado)':<15} | {'i/N':<10} | {'|i/N - xi|':<10}")
    print("-" * 55)
    
    d_max = 0
    for i in range(N):
        posicion = i + 1
        i_sobre_n = posicion / N
        distancia = abs(i_sobre_n - numeros_ordenados[i])
        
        if distancia > d_max:
            d_max = distancia
            
        print(f"{posicion:<4} | {numeros_ordenados[i]:<15.5f} | {i_sobre_n:<10.6f} | {distancia:<10.6f}")

    print("-" * 55)
    print(f"-> Estadístico calculado (D_max): {d_max:.6f}")

    # Paso 5: Buscar estadístico de tablas (d_alfa, N)
    alfa = a / 100.0
    # ksone.ppf nos da el valor crítico para un nivel de confianza
    d_tabla = stats.ksone.ppf(1 - alfa, N)
    
    print(f"-> Estadístico de tablas (d_{alfa:.3f}, {N}): {d_tabla:.6f}")

    # Paso 6: Comparación final
    print(f"\n======================================")
    print(f" CONCLUSIÓN")
    print(f"======================================")
    if d_max < d_tabla:
        print(f"✅ ACEPTADOS: Como {d_max:.6f} < {d_tabla:.6f},")
        print("Los números son aceptados (provienen de una distribución uniforme).")
    else:
        print(f"❌ RECHAZADOS: Como {d_max:.6f} >= {d_tabla:.6f},")
        print("Los números se rechazan (no son uniformes).")

# ==========================================
# MENÚ DE ENTRADA
# ==========================================
if __name__ == "__main__":
    print("=== CONFIGURACIÓN PRUEBA K-S ===")
    try:
        n = int(input("N (Cantidad de números): "))
        a = float(input("A (Porcentaje de significancia α, ej. 5): "))
        col = int(input("COL (Número de columna, 1-10): "))
        reng = int(input("RENG (Renglón de inicio, bloques de 5 filas): "))
        
        # Ruta según tu estructura de carpetas
        ruta_archivo = 'DATOS/NUMEROS_ALEATORIOS.csv'
        
        datos, alpha = cargar_numeros(ruta_archivo, n, a, col, reng)
        
        if datos:
            prueba_kolmogorov(datos, alpha)
            
    except ValueError:
        print("Error: Ingresa valores numéricos válidos.")