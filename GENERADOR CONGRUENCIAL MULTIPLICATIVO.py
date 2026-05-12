import math

def analizar_modulo(m):
    # Detección de Binario (Potencia de 2)
    if (m & (m - 1) == 0) and m > 0:
        d = int(math.log2(m))
        return "Binario", m // 4
    
    # Detección de Decimal (Potencia de 10)
    log10 = math.log10(m)
    if log10.is_integer():
        d = int(log10)
        if d >= 5:
            pe = 5 * (10**(d - 2))
        else:
            # Cálculo de lambda para d < 5
            l5 = (5**(d-1)) * 4
            l2 = 2 if d == 1 or d == 2 else 2**(d-2)
            pe = math.lcm(l5, l2) # MCM
        return "Decimal", pe
    
    return "Especial", m

def generador_congruencial_multiplicativo(a, x0, m):
    # 1. Analizar el módulo antes de empezar
    tipo, pe = analizar_modulo(m)
    
    print(f"\n--- Analizar Periodo Esperado ---")
    print(f"Tipo de módulo detectado: {tipo}")
    print(f"Periodo esperado (P.E.): {pe}")
    print("-" * 50)
    
    # 2. Encabezado de la tabla
    print(f"{'i':<5} | {'Xn':<5} | {'Formula':<15} | {'Xn+1':<5} | {'Ui':<8}")
    print("-" * 50)
    
    xn = x0
    # Usamos pe (periodo esperado) para saber cuántas iteraciones valen la pena
    for i in range(pe):
        resultado_operacion = (a * xn)
        resultado_division = resultado_operacion // m
        xn_siguiente = resultado_operacion % m
        ui = xn_siguiente / m
        
        formula_str = f"{resultado_division} + {xn_siguiente}/{m}"
        print(f"{i+1:<5} | {xn:<5} | {formula_str:<15} | {xn_siguiente:<5} | {ui:<8.6f}")
        
        xn = xn_siguiente

    print("")

# --- Entrada de datos ---
print("\nGenerador Congruencial Multiplicativo")
A = int(input("a: "))
X0 = int(input("x0: "))
M = int(input("m: "))

generador_congruencial_multiplicativo(A, X0, M)