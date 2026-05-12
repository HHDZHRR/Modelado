def generador_congruencial_mixto(a, x0, c, m):
    print(f"\n{'i':<5} | {'Xn':<5} | {'Formula':<10} | {'Xn+1':<5} | {'Ui':<8}")
    print("-" * 46)
    
    xn = x0
    for i in range(m):
        # Aplicamos la fórmula: (a * Xn + c) % m
        resultado_operacion = (a * xn) + c
        resultado_division = resultado_operacion // m
        xn_siguiente = resultado_operacion % m
        ui = xn_siguiente / m # Número pseudoaleatorio entre 0 y 1
        
        formula_str = f"{resultado_division} + {xn_siguiente}/{m}"
        print(f"{i+1:<5} | {xn:<5} | {formula_str:<10} | {xn_siguiente:<5} | {ui:<8.6f}")
        
        xn = xn_siguiente
    print(f"\nx0 = {x0}, xn = {xn}.\n")

# Parámetros del ejercicio
print("\nGenerador Congruencial Mixto")
A = int(input("a: "))
X0 = int(input("x0: "))
C = int(input("c: "))
M = int(input("m: "))

generador_congruencial_mixto(A, X0, C, M)