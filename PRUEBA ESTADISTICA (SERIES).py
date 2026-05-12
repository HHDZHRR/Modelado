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
                    numeros.append(float("0." + valor_texto))
        return numeros, a
    except Exception as e:
        print(f"Error al cargar: {e}")
        return None, None

def prueba_series(numeros, a, n_sub):
    N = len(numeros)
    if N < 2: 
        print("Se necesitan al menos 2 números para formar parejas.")
        return

    # 1. MOSTRAR NÚMEROS
    print(f"\n======================================")
    print(f" 1. NÚMEROS EXTRAÍDOS (N={N})")
    print(f"======================================")
    for i in range(0, len(numeros), 5):
        print(numeros[i:i+5])

    # 2. MOSTRAR PAREJAS
    print(f"\n======================================")
    print(f" 2. PAREJAS FORMADAS (N-1 = {N-1})")
    print(f"======================================")
    parejas = []
    for i in range(N - 1):
        p = (numeros[i], numeros[i+1])
        parejas.append(p)
        print(f"Pareja {i+1}: {p}")

    # 3. CÁLCULOS
    print(f"\n======================================")
    print(f" 3. MATRIZ DE FRECUENCIAS (FOi)")
    print(f"======================================")
    
    # Frecuencia Esperada FEi = (N-1) / n^2 [cite: 51]
    fe = (N - 1) / (n_sub ** 2)
    print(f"Frecuencia Esperada (FE): {fe:.4f}\n")
    
    # Inicializar matriz de ceros
    fo = [[0] * n_sub for _ in range(n_sub)]
    
    # Ubicar parejas en la cuadrícula 
    for x, y in parejas:
        c = int(x * n_sub)
        f = int(y * n_sub)
        if c == n_sub: c -= 1
        if f == n_sub: f -= 1
        fo[f][c] += 1

    # Imprimir la matriz visualmente
    for fila in reversed(fo): # reversed para que el 0,0 esté abajo a la izquierda
        print(fila)
    
    print(f"\n{ '-' * 55}\n")
    
    # 4. ESTADÍSTICO X0^2 [cite: 55]
    suma_cuadrados = 0
    for fila in range(n_sub):
        for col in range(n_sub):
            suma_cuadrados += (fo[fila][col] - fe)**2
            print(f"(FO - FE) = {fo[fila][col]} - {fe:.6f}       |       (FO - FE)^2 = {(fo[fila][col] - fe)**2:.6f}")
            
    x0_cuadrado = (n_sub**2 / (N - 1)) * suma_cuadrados
    
    # 5. TABLAS [cite: 56]
    alfa = a / 100.0
    gl = (n_sub**2) - 1
    x_tabla = stats.chi2.ppf(1 - alfa, gl)

    print(f"\n{ '-' * 55}\n")
    print("Estadístico calculado (X0^2):")
    print(f"{"":<3}X0^2) = {n_sub**2}/{N - 1} [{suma_cuadrados}]")
    print(f"{"":<3}X0^2) = {(n_sub**2) / (N - 1)} [{suma_cuadrados}]")
    print(f"-> X0^2) = {x0_cuadrado:.6f}")
    print(f"\nEstadístico de tablas (X^2 {alfa}, {gl}): {x_tabla:.4f}")

    # 6. CONCLUSIÓN [cite: 57]
    if x0_cuadrado < x_tabla:
        print(f"\n✅ ACEPTADOS: {x0_cuadrado:.5f} < {x_tabla:.5f}")
        print("La distribución espacial de las parejas es uniforme.")
    else:
        print(f"\n❌ RECHAZADOS: {x0_cuadrado:.5f} >= {x_tabla:.5f}")
        print("Las parejas tienden a agruparse; no hay aleatoriedad suficiente.")

if __name__ == "__main__":
    try:
        n = int(input("N (Cantidad de números): "))
        a = float(input("A (Significancia α, ej. 5): "))
        k = int(input("Subintervalos por eje (n): ")) # La cuadrícula será de n x n
        col = int(input("COL (1-10): "))
        reng = int(input("RENG (Bloque de 5): "))
        
        ruta = 'DATOS/NUMEROS_ALEATORIOS.csv'
        datos, alpha = cargar_numeros(ruta, n, a, col, reng)
        
        if datos:
            prueba_series(datos, alpha, k)
    except ValueError:
        print("Error: Ingresa datos numéricos válidos.")