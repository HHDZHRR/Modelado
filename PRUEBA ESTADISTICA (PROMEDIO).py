import csv
import math
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
            
            for i in range(fila_inicio, min(fila_inicio + n, len(filas))):
                if col_idx < len(filas[i]):
                    valor_texto = filas[i][col_idx].strip()
                    # Convertir texto a decimal 0.XXXXX
                    valor_decimal = float("0." + valor_texto)
                    numeros.append(valor_decimal)
                    
        print(f"\n======================================")
        print(f" DATOS EXTRAÍDOS")
        print(f"======================================")
        print(f"Se extrajeron: {len(numeros)} números")
        print(f"Lista: {numeros}")
        
        return numeros, a
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{archivo}'.")
        return None, None

def prueba_promedio(numeros, a):
    """
    Aplica la Prueba de Promedio según el documento PDF.
    """
    N = len(numeros)
    if N == 0:
        print("No hay números para analizar.")
        return
        
    print(f"\n======================================")
    print(f" 1. PRUEBA DE PROMEDIO")
    print(f"======================================")
    
    # Paso 2: Calcular el promedio (Media)
    promedio = sum(numeros) / N
    print(f"-> La suma total de los números: {sum(numeros):.5f}")
    print(f"-> Promedio de los números (x̄): {promedio:.6f}")
    print("")
    
    # Paso 3: Calcular el estadístico Z0
    # z_0 = | ((x̄ - 1/2) * sqrt(N)) / sqrt(1/12) |
    z_0 = abs((promedio - 0.5) * math.sqrt(N) / math.sqrt(1/12))
    print(f"Estadístico calculado:")
    print(f"{"":<3}Z_0 = [({promedio:.6f} - 0.5) * sqrt({N})] / sqrt(1/12)")
    print(f"{"":<3}Z_0 = [({(promedio - 0.5):.6f}) * {math.sqrt(N):.6f}] / {math.sqrt(1/12):.6f}")
    print(f"{"":<3}Z_0 = [{((promedio - 0.5) * math.sqrt(N)):.6f}] / {math.sqrt(1/12):.6f}")
    print(f"-> Z_0 = {z_0:.6f}")
    print("")
    
    # Paso 4: Buscar el estadístico de tablas Z_(alfa/2)
    alfa = a / 100.0  # Convertimos porcentaje a decimal (ej. 5 -> 0.05)
    alfa_medios = alfa / 2
    
    # stats.norm.ppf busca el valor de Z en la tabla normal estándar
    z_tabla = abs(stats.norm.ppf(alfa_medios))
    print(f"Estadístico de tablas (Z_α/2 con α={a}%):")
    print(f"{"":<3}Z_{(1-alfa):.2f}/2")
    print(f"-> Z_{((1-alfa)/2):.3f} = {z_tabla:.3f}")

    # Paso 5: Conclusión
    print(f"\n======================================")
    print(f" CONCLUSIÓN DE LA PRUEBA")
    print(f"======================================")
    # Condición de aceptación: z_0 < z_tabla
    if z_0 < z_tabla:
        print(f"✅ ACEPTADOS: Como {z_0:.6f} < {z_tabla:.3f},")
        print("Los números provienen de una distribución uniforme y pueden usarse en la simulación.\n")
    else:
        print(f"❌ RECHAZADOS: Como {z_0:.6f} >= {z_tabla:.3f},")
        print("Los números NO provienen de una distribución uniforme y no pueden usarse.\n")

# ==========================================
# MENÚ PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("=== CONFIGURACIÓN DE PRUEBAS ESTADÍSTICAS ===")
    try:
        n = int(input("N (Cantidad de números): "))
        a = float(input("A (Porcentaje de significancia α, ej. 5): "))
        col = int(input("COL (Número de columna, 1-10): "))
        reng = int(input("RENG (Renglón de inicio, en bloques de 5 filas): "))
        
        # Cargar archivo y ejecutar prueba
        # Nota: El archivo extraído en el paso anterior se llama 'NUMEROS_ALEATORIOS.csv'
        datos, alpha = cargar_numeros('DATOS/NUMEROS_ALEATORIOS.csv', n, a, col, reng)
        
        if datos:
            prueba_promedio(datos, alpha)
            
    except ValueError:
        print("Error: Por favor ingresa solo datos numéricos.")