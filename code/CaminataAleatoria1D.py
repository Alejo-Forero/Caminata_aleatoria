import json
import matplotlib.pyplot as plt
import sys
import os


from pruebas.Generador import generar

# Importar las funciones de pruebas directamente
from pruebas.prueba_de_medias import prueba_de_medias
from pruebas.prueba_de_varianza import prueba_de_varianza
from pruebas.prueba_chi2_2 import prueba_chi_cuadrado
from pruebas.ks import kolmogorov_smirnov_test
from pruebas.poker import poker_test_json
from pruebas.rachas import prueba_rachas

# Diccionario de pruebas disponibles
PRUEBAS_DISPONIBLES = {
    "medias": prueba_de_medias,
    "varianza": prueba_de_varianza,
    "chi": prueba_chi_cuadrado,
    "kolmogorov": kolmogorov_smirnov_test,
    "poker": poker_test_json,
    "rachas": prueba_rachas
}

def ejecutar_pruebas(datos, pruebas, alpha):
    """Ejecuta las pruebas estadísticas seleccionadas"""
    resultados = {}
    for nombre, info in pruebas.items():
        if nombre == "kolmogorov" and info != False and nombre in PRUEBAS_DISPONIBLES:
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, k=info.get("k"), alpha=alpha)
        elif nombre == "chi" and info != False and nombre in PRUEBAS_DISPONIBLES:
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, k=info.get("k"), alpha=alpha)
        elif info and nombre in PRUEBAS_DISPONIBLES:
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, alpha=alpha)
    return resultados

def obtener_parametros():
    """Obtiene los parámetros del usuario para la generación de números"""
    print("=== GENERACIÓN DE NÚMEROS PSEUDOALEATORIOS ===")
    print("Ingrese los parámetros para el generador congruencial lineal:")

    try:
        x_o = int(input("Semilla inicial (x_0): "))
        k = int(input("Parámetro k: "))
        c = int(input("Constante aditiva (c): "))
        g = int(input("Exponente de módulo (g) donde m = 2^g: "))
        n = int(input("Cantidad de números a generar: "))

        if n < 10:
            print("Advertencia: Se recomienda al menos 10 números para las pruebas estadísticas")

        return x_o, k, c, g, n
    except ValueError:
        print("Error: Ingrese solo números enteros")
        return obtener_parametros()

def configurar_pruebas():
    print("\n=== CONFIGURACIÓN DE PRUEBAS ESTADÍSTICAS ===")
    print("¿Qué pruebas desea ejecutar? (s/n)")

    pruebas = {}

    pruebas["medias"] = input("Prueba de Medias (s/n): ").lower().startswith('s')
    pruebas["varianza"] = input("Prueba de Varianza (s/n): ").lower().startswith('s')
    pruebas["rachas"] = input("Prueba de Rachas (s/n): ").lower().startswith('s')
    pruebas["poker"] = input("Prueba de Póker (s/n): ").lower().startswith('s')

    if input("Prueba Chi-Cuadrado (s/n): ").lower().startswith('s'):
        k = int(input("  Número de intervalos (k): "))
        pruebas["chi"] = {"k": k}
    else:
        pruebas["chi"] = False

    if input("Prueba Kolmogorov-Smirnov (s/n): ").lower().startswith('s'):
        k = int(input("  Número de intervalos (k): "))
        pruebas["kolmogorov"] = {"k": k}
    else:
        pruebas["kolmogorov"] = False

    alpha = float(input("Nivel de significancia (alpha, ej: 0.05): ") or "0.05")

    return pruebas, alpha

def mostrar_resultados_pruebas(resultados):
    print("\n=== RESULTADOS DE PRUEBAS ESTADÍSTICAS ===")

    pruebas_pasadas = 0
    total_pruebas = 0

    for nombre, resultado_json in resultados.items():
        try:
            resultado = json.loads(resultado_json)
            total_pruebas += 1

            aprobado = resultado.get("isApproved", "False").lower() == "true"
            if aprobado:
                pruebas_pasadas += 1
                status = "PASÓ"
            else:
                status = "NO PASÓ"

            print(f"\n{resultado['test_name']}: {status}")
            print(f"  Decisión: {resultado['decision']}")

            # Mostrar estadísticas clave según el tipo de prueba
            if 'statistics' in resultado:
                stats = resultado['statistics']
                if 'chi2_total' in stats:
                    print(f"  Chi² calculado: {stats['chi2_total']:.4f}")
                    print(f"  Chi² crítico: {stats['chi2_critico']:.4f}")
                elif 'max_difference' in stats:
                    print(f"  Diferencia máxima: {stats['max_difference']:.4f}")
                    print(f"  Valor crítico: {stats['critical_value']:.4f}")
                elif 'Chi2_calculado' in stats:
                    print(f"  Chi² calculado: {stats['Chi2_calculado']:.4f}")
                    print(f"  Valor crítico: {stats['critical_value']:.4f}")

        except json.JSONDecodeError:
            print(f"{nombre}: Error al procesar resultado")

    print(f"\nRESUMEN: {pruebas_pasadas}/{total_pruebas} pruebas pasadas")

    return pruebas_pasadas == total_pruebas

def obtener_numero_pasos(max_pasos):
    """Obtiene el número de pasos que el usuario quiere simular"""
    while True:
        try:
            pasos = int(input(f"¿Cuántos pasos quiere que dé la rana? (máximo {max_pasos}): "))
            if 1 <= pasos <= max_pasos:
                return pasos
            else:
                print(f"Error: El número de pasos debe estar entre 1 y {max_pasos}")
        except ValueError:
            print("Error: Ingrese un número entero válido")

def simular_caminata(numeros_aleatorios, posicion_inicial=0, num_pasos=None):
    """Simula la caminata aleatoria de la rana"""
    if num_pasos is None:
        num_pasos = len(numeros_aleatorios)

    # Usar solo los primeros num_pasos números
    numeros_a_usar = numeros_aleatorios[:num_pasos]

    print(f"\n=== SIMULACIÓN DE CAMINATA ALEATORIA ===")
    print(f"Posición inicial: {posicion_inicial}")
    print(f"Probabilidad de avanzar: 0.5")
    print(f"Número de pasos a simular: {num_pasos}")
    print(f"Números disponibles: {len(numeros_aleatorios)}")

    posiciones = [posicion_inicial]
    posicion_actual = posicion_inicial

    print("\nPasos de la rana:")
    for i, numero in enumerate(numeros_a_usar):
        if numero >= 0.5:
            posicion_actual += 1
            movimiento = "→ (+1)"
        else:
            posicion_actual -= 1
            movimiento = "← (-1)"

        posiciones.append(posicion_actual)
        print(f"Paso {i+1:2d}: r={numero:.5f} {movimiento} → Posición: {posicion_actual}")

    return posiciones

def graficar_caminata(posiciones):
    """Grafica la trayectoria de la rana"""
    pasos = list(range(len(posiciones)))

    plt.figure(figsize=(12, 6))
    plt.plot(pasos, posiciones, 'b-o', linewidth=2, markersize=4)
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Posición inicial')

    plt.xlabel('Número de Pasos')
    plt.ylabel('Posición de la Rana')
    plt.title('Caminata Aleatoria de una Rana')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Anotaciones
    plt.annotate(f'Inicio\nPos: {posiciones[0]}',
                 xy=(0, posiciones[0]), xytext=(5, posiciones[0]+0.5),
                 arrowprops=dict(arrowstyle='->', color='green'))

    plt.annotate(f'Final\nPos: {posiciones[-1]}',
                 xy=(len(posiciones)-1, posiciones[-1]),
                 xytext=(len(posiciones)-6, posiciones[-1]+0.5),
                 arrowprops=dict(arrowstyle='->', color='red'))

    plt.tight_layout()
    plt.show()

    # Estadísticas de la caminata
    desplazamiento_final = posiciones[-1] - posiciones[0]
    distancia_maxima = max(posiciones) - min(posiciones)

    print(f"\nESTADÍSTICAS DE LA CAMINATA:")
    print(f"  Posición inicial: {posiciones[0]}")
    print(f"  Posición final: {posiciones[-1]}")
    print(f"  Desplazamiento neto: {desplazamiento_final}")
    print(f"  Rango de posiciones: [{min(posiciones)}, {max(posiciones)}]")
    print(f"  Distancia total recorrida: {len(posiciones)-1} pasos")

def main():
    print("SIMULADOR DE CAMINATA ALEATORIA DE UNA RANA")
    print("=" * 50)

    x_o, k, c, g, n = obtener_parametros()

    print(f"\nenerando {n} números pseudoaleatorios...")
    df = generar(x_o, k, c, g, n)
    numeros = df['Ri'].tolist()
    print(f"Números generados exitosamente")
    print(f"Primeros 5 números: {numeros[:5]}")

    pruebas, alpha = configurar_pruebas()

    if any(pruebas.values()):
        print(f"\nEjecutando pruebas estadísticas...")
        resultados = ejecutar_pruebas(numeros, pruebas, alpha)

        todas_pasaron = mostrar_resultados_pruebas(resultados)

        if not todas_pasaron:
            print("\nADVERTENCIA: No todos los números pasaron las pruebas estadísticas")
            continuar = input("¿Desea continuar con la simulación de todos modos? (s/n): ")
            if not continuar.lower().startswith('s'):
                print("Simulación cancelada. Intente con otros parámetros.")
                return
    else:
        print("No se ejecutaron pruebas estadísticas")
        continuar = input("¿Desea continuar sin pruebas? (s/n): ")
        if not continuar.lower().startswith('s'):
            return

    print(f"\nIniciando simulación de caminata aleatoria...")
    posicion_inicial = int(input("Posición inicial de la rana (0): ") or "0")

    # Obtener número de pasos
    num_pasos = obtener_numero_pasos(len(numeros))

    posiciones = simular_caminata(numeros, posicion_inicial, num_pasos)

    print(f"\nGenerando gráfica...")
    graficar_caminata(posiciones)

    print(f"\nSimulación completada exitosamente!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulación interrumpida por el usuario")
    except Exception as e:
        print(f"\nError inesperado: {e}")
