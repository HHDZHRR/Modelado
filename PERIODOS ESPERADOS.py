import math

def analizar_modulo(m):
    # Detección de Binario (Potencia de 2)
    if (m & (m - 1) == 0) and m > 0:
        d = int(math.log2(m))
        formula_str = f"p.e. = m/4 \n{"":<14}= {m}/{4}"
        return "Binario", formula_str, m // 4
    
    # Detección de Decimal (Potencia de 10)
    log10 = math.log10(m)
    if log10.is_integer():
        d = int(log10)
        if d >= 5:
            pe = 5 * (10**(d - 2))
            formula_str = f"p.e. = 5x10^(d-2) \n{"":<14}= 5x10^({d}-2) \n{"":<14}= 5x10^({d-2})"
        else:
            # Cálculo de lambda para d < 5
            l5 = (5**(d-1)) * 4
            l2 = 2 if d == 1 else 2**(d-2)
            pe = math.lcm(l5, l2) # MCM
            formula_str = f"p.e. = mcm[5^(d-1)x4, 2^(d-2)] \n{"":<14}= mcm[5^({d-1})x4, 2^({d-2 if d > 1 else d})] \n{"":<14}= mcm[{l5}, {l2}]"
        return "Decimal", formula_str, pe
    
    return "Especial", "Error", m

def periodos_esperados(m):
    # 1. Analizar el módulo antes de empezar
    tipo, formula, pe = analizar_modulo(m)
    
    print(f"\nTipo de módulo detectado: {tipo}")
    print(f"Fórmula: {formula}")
    print(f"Periodo esperado (P.E.): {pe}\n")

# --- Entrada de datos ---
print("\nPeriodos Esperados")
M = int(input("m: "))

periodos_esperados(M)