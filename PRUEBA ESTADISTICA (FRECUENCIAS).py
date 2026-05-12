import csv
import scipy.stats as stats

def cargar_numeros(archivo, n, a, col, reng):
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
                    valor_decimal = float("0." + valor_texto)
                    numeros.append(valor_decimal)
        return numeros, a
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo.")
        return None, None

def prueba_frecuencias(numeros, a, num_intervalos):
    """
    Aplica la Prueba de Frecuencias según el PDF.
    """
    N = len(numeros)
    if N == 0: return

    # --- NUEVA SECCIÓN: MOSTRAR NÚMEROS OBTENIDOS ---
    print(f"\n======================================")
    print(f" LISTA DE NÚMEROS OBTENIDOS (N={N})")
    print(f"======================================")
    # Imprime los números en grupos de 5 para que no sea una lista infinita hacia abajo
    for i in range(0, len(numeros), 5):
        print(numeros[i:i+5])

    print(f"\n======================================")
    print(f" PRUEBA DE FRECUENCIAS")
    print(f"======================================")

    # Paso 3: Calcular frecuencia esperada (FEi = N / n)
    fe = N / num_intervalos
    
    # Paso 4: Definir límites y contar frecuencias observadas (FOi)
    fo = [0] * num_intervalos
    for num in numeros:
        # Determinamos a qué intervalo pertenece el número
        intervalo = int(num * num_intervalos)
        if intervalo == num_intervalos: # Caso borde para el número 1.0
            intervalo -= 1
        fo[intervalo] += 1

    # Paso 5: Calcular el estadístico X0^2 = (1/FE) * sum((FOi - FEi)^2)
    suma_cuadrados = 0
    print(f"\n{'Intervalo':<12} | {'Límites':<3} | {'FOi':<6} | {'FEi':<6} | {'(FOi-FEi)^2':<12}")
    print("-" * 55)
    
    for i in range(num_intervalos):
        lim_inf = i / num_intervalos
        lim_sup = (i + 1) / num_intervalos
        suma_cuadrados += (fo[i] - fe)**2
        print(f"{i+1:<12} | {lim_inf:.2f}-{lim_sup:.2f} | {fo[i]:<6} | {fe:<6.2f} | {((fo[i] - fe)**2):<12.5f}")

    x0_cuadrado = (1 / fe) * suma_cuadrados
    print("-" * 55)
    print("Estadístico calculado (X0^2):")
    print(f"{"":<3}X0^2 = 1/FEi * sum((FOi - FEi)^2)")
    print(f"{"":<3}X0^2 = ({(1 / fe):.5f}) * ({suma_cuadrados:.5f})")
    print(f"-> X0^2 = {x0_cuadrado:.5f}")

    # Paso 6: Buscar estadístico de tablas Chi-cuadrada (X^2 alfa, n-1)
    alfa = a / 100.0
    grados_libertad = num_intervalos - 1
    # stats.chi2.ppf usa el área a la izquierda, por eso 1 - alfa
    x_tabla = stats.chi2.ppf(1 - alfa, grados_libertad)
    
    print(f"\nEstadístico de tablas (X^2 {alfa}, {grados_libertad}): {x_tabla:.4f}")

    # Paso 7: Comparación
    print(f"\n======================================")
    print(f" CONCLUSIÓN")
    print(f"======================================")
    if x0_cuadrado < x_tabla:
        print(f"✅ ACEPTADOS: Como {x0_cuadrado:.5f} < {x_tabla:.5f}, los números son uniformes.")
    else:
        print(f"❌ RECHAZADOS: Como {x0_cuadrado:.5f} >= {x_tabla:.5f}, los números no son uniformes.")

if __name__ == "__main__":
    try:
        n = int(input("N (Cantidad de números): "))
        a = float(input("A (Porcentaje α, ej. 5): "))
        k = int(input("Número de subintervalos (n): "))
        col = int(input("COL (Columna 1-10): "))
        reng = int(input("RENG (Renglón de inicio): "))
        
        ruta = 'DATOS/NUMEROS_ALEATORIOS.csv'
        datos, alpha = cargar_numeros(ruta, n, a, col, reng)
        
        if datos:
            prueba_frecuencias(datos, alpha, k)
            
    except ValueError:
        print("Error: Ingresa datos válidos.")