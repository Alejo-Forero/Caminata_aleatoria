import json
from collections import Counter
import scipy.stats as stats

def poker_test_json(datos, alpha=0.05):
    """
    numbers: lista de números pseudoaleatorios
    Retorna un JSON con la estructura de la prueba de póker.
    """
    n = len(datos)

    # Probabilidades teóricas
    probs = {
        "D": 0.3024,   # Todos diferentes
        "O": 0.504,    # Un par
        "T": 0.108,    # Dos pares
        "K": 0.072,    # Tercia
        "F": 0.009,    # Full
        "P": 0.0045,   # Poker
        "Q": 0.0001    # Quintilla
    }

    # Clasificación de cada número
    def classify(num):
        digits = list(str(num).replace("0.", ""))[:5]  # tomamos 5 dígitos
        counts = sorted(Counter(digits).values(), reverse=True)

        if counts == [5]:
            return "Q"  # Quintilla
        elif counts == [4,1]:
            return "P"  # Poker
        elif counts == [3,2]:
            return "F"  # Full
        elif counts == [3,1,1]:
            return "K"  # Tercia
        elif counts == [2,2,1]:
            return "T"  # Dos pares
        elif counts == [2,1,1,1]:
            return "O"  # Un par
        else:
            return "D"  # Todos diferentes

    # Recuento de observados
    observed = {cat: 0 for cat in probs}
    for num in datos:
        cat = classify(num)
        observed[cat] += 1

    # Esperados
    expected = {cat: n * p for cat, p in probs.items()}

    # Estructura de datos similar a la tabla
    categories_data = []
    suma_oi = 0
    suma_chi2 = 0
    
    for cat in ["D", "O", "T", "K", "F", "P", "Q"]:
        oi = observed[cat]
        prob = probs[cat]
        ei = expected[cat]
        
        # Cálculo de (Oi-Ei)^2 / Ei solo si Ei > 0
        chi2_component = ((oi - ei)**2) / ei if ei > 0 else 0
        chi2_component = chi2_component
        
        categories_data.append({
            "Cat": cat,
            "Oi": oi,
            "Prob": prob,
            "Ei": ei,
            "(Oi-Ei)^2/Ei": chi2_component
        })
        
        suma_oi += oi
        suma_chi2 += chi2_component

    # Valor crítico (gl = categorias-1 = 6, alfa=0.05 → 12.59 aprox.)
    chi2_critical = stats.chi2.ppf(1 - alpha, 6)

    result = {
        "test_name": "Prueba de Poker",
        "intervals_data": categories_data,
        "statistics": {
            "Suma_Oi": suma_oi,
            "Chi2_calculado": suma_chi2,
            "critical_value": chi2_critical
        },      
        "decision": "Pasa la prueba de poker." if suma_chi2 <= chi2_critical else "No pasa la prueba de poker.",
        "isApproved": str(suma_chi2 <= chi2_critical)
    }

    return json.dumps(result, indent=4, ensure_ascii=False)
