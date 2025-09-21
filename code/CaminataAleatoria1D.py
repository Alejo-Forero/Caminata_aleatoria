# Este programa simula la caminata aleatoria de una rana usando números
# pseudoaleatorios generados con un generador congruencial lineal y
# validados mediante pruebas estadísticas.
import json                 # Manejo de archivos JSON para persistencia de datos
import matplotlib.pyplot as plt  # Generación de gráficas y visualizaciones
import os                   # Operaciones del sistema de archivos
import numpy as np          # Cálculos matemáticos y estadísticos eficientes
import time                 # Medición de tiempos de ejecución

# Importación del generador de números pseudoaleatorios personalizado
from pruebas.generador import generar
# Importación de todas las funciones de pruebas estadísticas disponibles
from pruebas.prueba_de_medias import prueba_de_medias          # Prueba t de medias
from pruebas.prueba_de_varianza import prueba_de_varianza      # Prueba chi-cuadrado de varianza
from pruebas.prueba_chi2_2 import prueba_chi_cuadrado         # Prueba chi-cuadrado de uniformidad
from pruebas.ks import kolmogorov_smirnov_test                # Prueba Kolmogorov-Smirnov
from pruebas.poker import poker_test_json                     # Prueba de póker para aleatoriedad
from pruebas.rachas import prueba_rachas                      # Prueba de rachas ascendentes/descendentes

# Nombre del archivo JSON donde se almacenan las posiciones finales de todas las simulaciones
ARCHIVO_HISTORICO = "caminatas.json"

# Diccionario que mapea nombres de pruebas estadísticas a sus funciones correspondientes
# Esto permite ejecutar dinámicamente las pruebas seleccionadas por el usuario
PRUEBAS_DISPONIBLES = {
    "medias": prueba_de_medias,              # Verifica si la media está cerca de 0.5
    "varianza": prueba_de_varianza,          # Verifica si la varianza está cerca de 1/12
    "chi": prueba_chi_cuadrado,             # Verifica uniformidad usando chi-cuadrado
    "kolmogorov": kolmogorov_smirnov_test,   # Verifica uniformidad usando K-S
    "poker": poker_test_json,               # Verifica aleatoriedad mediante patrones
    "rachas": prueba_rachas                 # Verifica independencia de números consecutivos
}

def cargar_historico():
    """
    Carga el histórico de posiciones finales desde el archivo JSON.

    Returns:
        list: Lista de enteros representando las posiciones finales de simulaciones anteriores.
              Si el archivo no existe o está corrupto, retorna una lista vacía.
    """
    try:
        # Verificar si el archivo existe antes de intentar abrirlo
        if os.path.exists(ARCHIVO_HISTORICO):
            with open(ARCHIVO_HISTORICO, 'r', encoding='utf-8') as f:
                return json.load(f)  # Cargar y retornar los datos del JSON
        else:
            return []  # Archivo no existe, retornar lista vacía
    except (json.JSONDecodeError, FileNotFoundError):
        # Manejar archivos corruptos o errores de lectura
        print("Archivo de histórico corrupto o no encontrado. Creando nuevo histórico.")
        return []

def guardar_historico(posiciones_finales):
    """
    Guarda el histórico de posiciones finales en el archivo JSON.

    Args:
        posiciones_finales (list): Lista de enteros con las posiciones finales a guardar.

    Returns:
        bool: True si el guardado fue exitoso, False en caso contrario.
    """
    try:
        # Escribir al archivo con formato legible (indent=2 para mejor presentación)
        with open(ARCHIVO_HISTORICO, 'w', encoding='utf-8') as f:
            json.dump(posiciones_finales, f, indent=2)
        return True  # Guardado exitoso
    except Exception as e:
        print(f"Error al guardar histórico: {e}")
        return False  # Error en el guardado

def agregar_posicion_final_al_historico(posicion_final):
    """
    Agrega una nueva posición final al histórico existente.

    Args:
        posicion_final (int): La posición final de la rana en la simulación actual.

    Returns:
        bool: True si se agregó exitosamente, False en caso contrario.
    """
    # Cargar el histórico actual
    historico = cargar_historico()

    # Agregar la nueva posición final
    historico.append(posicion_final)

    # Guardar el histórico actualizado y mostrar feedback al usuario
    if guardar_historico(historico):
        print(f"\nPosición final guardada en el histórico: {posicion_final}")
        return True
    else:
        print("\nError al guardar la posición final en el histórico")
        return False

def generar_histograma_posiciones_finales():
    """
    Genera un histograma de las posiciones finales de todas las simulaciones guardadas.
    Incluye estadísticas descriptivas y una línea vertical mostrando la media.
    """
    # Cargar todas las posiciones finales del histórico
    posiciones_finales = cargar_historico()

    # Verificar si hay datos para analizar
    if not posiciones_finales:
        print("\nNo hay datos para generar el histograma")
        return

    # Crear el histograma con configuración profesional
    plt.figure(figsize=(10, 6))  # Tamaño de figura apropiado
    # Calcular número óptimo de bins (máximo 20 o número de valores únicos)
    num_bins = min(20, len(set(posiciones_finales)))
    plt.hist(posiciones_finales, bins=num_bins,
             alpha=0.7,           # Transparencia para mejor visualización
             color='skyblue',     # Color atractivo
             edgecolor='black')   # Bordes negros para definición
    # Agregar línea vertical para la media
    media = np.mean(posiciones_finales)
    plt.axvline(media, color='red', linestyle='--',
                label=f'Media: {media:.2f}')
    # Configurar etiquetas y título
    plt.xlabel('Posición Final')
    plt.ylabel('Frecuencia')
    plt.title(f'Histograma de Posiciones Finales\n({len(posiciones_finales)} simulaciones)')
    plt.legend()
    plt.grid(True, alpha=0.3)  # Grid sutil para mejor lectura
    plt.tight_layout()         # Ajuste automático de espacios
    plt.show()

    # Calcular y mostrar estadísticas descriptivas completas
    print(f"\nESTADÍSTICAS DE LAS POSICIONES FINALES:")
    print(f"  Total de simulaciones: {len(posiciones_finales)}")
    print(f"  Media: {np.mean(posiciones_finales):.3f}")
    print(f"  Desviación estándar: {np.std(posiciones_finales):.3f}")
    print(f"  Mediana: {np.median(posiciones_finales):.3f}")
    print(f"  Mínima: {min(posiciones_finales)}")
    print(f"  Máxima: {max(posiciones_finales)}")

def limpiar_historico():
    """
    Permite limpiar el histórico de posiciones finales con confirmación de seguridad.
    Requiere que el usuario escriba exactamente 'CONFIRMAR' para proceder.
    """
    # Verificar si hay datos para limpiar
    posiciones_finales = cargar_historico()

    if not posiciones_finales:
        print("\nNo hay datos para limpiar")
        return

    # Mostrar advertencia y solicitar confirmación
    print(f"\nADVERTENCIA: Esta acción eliminará todas las {len(posiciones_finales)} posiciones finales guardadas")
    confirmacion = input("¿Está seguro de que desea limpiar el histórico? (escriba 'CONFIRMAR' para continuar): ")

    # Verificar confirmación exacta (sensible a mayúsculas/minúsculas)
    if confirmacion == "CONFIRMAR":
        if guardar_historico([]):  # Guardar lista vacía
            print("Histórico limpiado exitosamente")
        else:
            print("Error al limpiar el histórico")
    else:
        print("Operación cancelada")

def menu_historico():
    """
    Muestra el menú de opciones del histórico con información actualizada.
    Permite generar histogramas, limpiar datos y volver al menú principal.
    """
    while True:
        # Cargar datos actualizados para mostrar el contador
        posiciones_finales = cargar_historico()

        # Mostrar menú con información actual
        print(f"\nMENÚ DE HISTÓRICO")
        print(f"{'='*30}")
        print(f"Simulaciones guardadas: {len(posiciones_finales)}")
        print("1. Generar histograma de posiciones finales")
        print("2. Limpiar histórico")
        print("3. Volver al menú principal")

        # Obtener y procesar la selección del usuario
        opcion = input("\nSeleccione una opción (1-3): ").strip()

        if opcion == "1":
            generar_histograma_posiciones_finales()
        elif opcion == "2":
            limpiar_historico()
        elif opcion == "3":
            break  # Salir del bucle para volver al menú principal
        else:
            print("Opción inválida. Por favor, seleccione entre 1 y 3.")

def ejecutar_pruebas(datos, pruebas, alpha):
    """
    Ejecuta las pruebas estadísticas seleccionadas sobre los números generados.

    Args:
        datos (list): Lista de números pseudoaleatorios a validar (floats entre 0 y 1).
        pruebas (dict): Diccionario con configuración de pruebas a ejecutar.
        alpha (float): Nivel de significancia para las pruebas (ej: 0.05 para 95% de confianza).

    Returns:
        dict: Diccionario con los resultados de cada prueba en formato JSON.
    """
    resultados = {}

    # Iterar sobre cada prueba configurada
    for nombre, info in pruebas.items():
        # Verificar que la prueba esté habilitada y disponible
        if nombre == "kolmogorov" and info != False and nombre in PRUEBAS_DISPONIBLES:
            # Kolmogorov-Smirnov requiere parámetro k (número de intervalos)
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, k=info.get("k"), alpha=alpha)

        elif nombre == "chi" and info != False and nombre in PRUEBAS_DISPONIBLES:
            # Chi-cuadrado también requiere parámetro k
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, k=info.get("k"), alpha=alpha)

        elif info and nombre in PRUEBAS_DISPONIBLES:
            # Otras pruebas solo requieren datos y alpha
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, alpha=alpha)

    return resultados

def mostrar_resultados_pruebas(resultados):
    """
    Muestra los resultados de las pruebas estadísticas de forma organizada.

    Args:
        resultados (dict): Diccionario con resultados en formato JSON de cada prueba.

    Returns:
        bool: True si todas las pruebas pasaron, False si alguna falló.
    """
    print("\n=== RESULTADOS DE PRUEBAS ESTADÍSTICAS ===")

    # Contadores para el resumen final
    pruebas_pasadas = 0
    total_pruebas = 0

    # Procesar cada resultado
    for nombre, resultado_json in resultados.items():
        try:
            # Parsear el JSON retornado por cada prueba
            resultado = json.loads(resultado_json)
            total_pruebas += 1

            # Determinar si la prueba fue aprobada
            aprobado = resultado.get("isApproved", "False").lower() == "true"
            if aprobado:
                pruebas_pasadas += 1
                status = "PASÓ"
            else:
                status = "NO PASÓ"

            # Mostrar información básica de la prueba
            print(f"\n{resultado['test_name']}: {status}")
            print(f"  Decisión: {resultado['decision']}")

            # Mostrar estadísticas específicas según el tipo de prueba
            if 'statistics' in resultado:
                stats = resultado['statistics']

                # Estadísticas para prueba Chi-cuadrado de uniformidad
                if 'chi2_total' in stats:
                    print(f"  Chi² calculado: {stats['chi2_total']:.4f}")
                    print(f"  Chi² crítico: {stats['chi2_critico']:.4f}")

                # Estadísticas para prueba Kolmogorov-Smirnov
                elif 'max_difference' in stats:
                    print(f"  Diferencia máxima: {stats['max_difference']:.4f}")
                    print(f"  Valor crítico: {stats['critical_value']:.4f}")

                # Estadísticas para otras pruebas chi-cuadrado
                elif 'Chi2_calculado' in stats:
                    print(f"  Chi² calculado: {stats['Chi2_calculado']:.4f}")
                    print(f"  Valor crítico: {stats['critical_value']:.4f}")

        except json.JSONDecodeError:
            # Manejar errores en el formato JSON
            print(f"{nombre}: Error al procesar resultado")

    # Mostrar resumen final
    print(f"\nRESUMEN: {pruebas_pasadas}/{total_pruebas} pruebas pasadas")

    # Retornar si todas las pruebas fueron exitosas
    return pruebas_pasadas == total_pruebas

def obtener_parametros():
    """
    Obtiene los parámetros del usuario para el generador congruencial lineal.
    Incluye validación de entrada y recomendaciones.

    Returns:
        tuple: (x_o, k, c, g, n) - Parámetros para el generador.
    """
    print("=== GENERACIÓN DE NÚMEROS PSEUDOALEATORIOS ===")
    print("Ingrese los parámetros para el generador congruencial lineal:")

    try:
        # Solicitar cada parámetro con descripción clara
        x_o = int(input("Semilla inicial (x_0): "))        # Valor inicial de la secuencia
        k = int(input("Parámetro k: "))                    # Multiplicador
        c = int(input("Constante aditiva (c): "))          # Incremento
        g = int(input("Exponente de módulo (g) donde m = 2^g: "))  # Para calcular m = 2^g
        n = int(input("Cantidad de números a generar: "))   # Tamaño de la muestra

        # Advertencia si n es muy pequeño para análisis estadístico confiable
        if n < 10:
            print("Advertencia: Se recomienda al menos 10 números para las pruebas estadísticas")

        return x_o, k, c, g, n

    except ValueError:
        # Manejar entradas no numéricas recursivamente
        print("Error: Ingrese solo números enteros")
        return obtener_parametros()

def configurar_pruebas():
    """
    Permite al usuario seleccionar qué pruebas estadísticas ejecutar.
    Algunas pruebas requieren parámetros adicionales.

    Returns:
        tuple: (pruebas, alpha) donde pruebas es dict con configuración y alpha es float.
    """
    print("\n=== CONFIGURACIÓN DE PRUEBAS ESTADÍSTICAS ===")
    print("¿Qué pruebas desea ejecutar? (s/n)")

    pruebas = {}

    # Pruebas simples (solo requieren respuesta s/n)
    pruebas["medias"] = input("Prueba de Medias (s/n): ").lower().startswith('s')
    pruebas["varianza"] = input("Prueba de Varianza (s/n): ").lower().startswith('s')
    pruebas["rachas"] = input("Prueba de Rachas (s/n): ").lower().startswith('s')
    pruebas["poker"] = input("Prueba de Póker (s/n): ").lower().startswith('s')

    # Prueba Chi-Cuadrado (requiere parámetro k)
    if input("Prueba Chi-Cuadrado (s/n): ").lower().startswith('s'):
        k = int(input("  Número de intervalos (k): "))
        pruebas["chi"] = {"k": k}  # Almacenar como diccionario con parámetros
    else:
        pruebas["chi"] = False

    # Prueba Kolmogorov-Smirnov (requiere parámetro k)
    if input("Prueba Kolmogorov-Smirnov (s/n): ").lower().startswith('s'):
        k = int(input("  Número de intervalos (k): "))
        pruebas["kolmogorov"] = {"k": k}
    else:
        pruebas["kolmogorov"] = False

    # Nivel de significancia (con valor por defecto)
    alpha = float(input("Nivel de significancia (alpha, ej: 0.05): ") or "0.05")

    return pruebas, alpha

def obtener_numero_pasos(max_pasos):
    """
    Obtiene el número de pasos que el usuario quiere simular.
    Incluye validación para no exceder los números disponibles.
    Args:
        max_pasos (int): Número máximo de pasos posibles (igual al número de números generados).
    Returns:
        int: Número de pasos válido seleccionado por el usuario.
    """
    while True:
        try:
            pasos = int(input(f"¿Cuántos pasos quiere que dé la rana? (máximo {max_pasos}): "))
            # Validar que esté en el rango permitido
            if 1 <= pasos <= max_pasos:
                return pasos
            else:
                print(f"Error: El número de pasos debe estar entre 1 y {max_pasos}")

        except ValueError:
            print("Error: Ingrese un número entero válido")

def simular_caminata(numeros_aleatorios, posicion_inicial=0, num_pasos=None):
    """
    Simula la caminata aleatoria de la rana usando números pseudoaleatorios.
    Args:
        numeros_aleatorios (list): Lista de números aleatorios entre 0 y 1.
        posicion_inicial (int): Posición de inicio de la rana (default: 0).
        num_pasos (int): Número de pasos a simular. Si None, usa todos los números.
    Returns:
        list: Lista de posiciones de la rana en cada paso (incluye posición inicial).
    """
    # Determinar cuántos pasos simular
    if num_pasos is None:
        num_pasos = len(numeros_aleatorios)

    # Usar solo los primeros num_pasos números
    numeros_a_usar = numeros_aleatorios[:num_pasos]

    # Mostrar información de la simulación
    print(f"\n=== SIMULACIÓN DE CAMINATA ALEATORIA ===")
    print(f"Posición inicial: {posicion_inicial}")
    print(f"Probabilidad de avanzar: 0.5")  # Umbral para decidir dirección
    print(f"Número de pasos a simular: {num_pasos}")
    print(f"Números disponibles: {len(numeros_aleatorios)}")

    # Inicializar variables de simulación
    posiciones = [posicion_inicial]  # Lista incluye posición inicial
    posicion_actual = posicion_inicial

    # Simular cada paso de la caminata
    print("\nPasos de la rana:")
    for i, numero in enumerate(numeros_a_usar):
        # Lógica de movimiento: >= 0.5 avanza, < 0.5 retrocede
        if numero >= 0.5:
            posicion_actual += 1
            movimiento = "→ (+1)"
        else:
            posicion_actual -= 1
            movimiento = "← (-1)"

        # Registrar nueva posición
        posiciones.append(posicion_actual)

        # Mostrar detalle de cada paso
        print(f"Paso {i+1:2d}: r={numero:.5f} {movimiento} → Posición: {posicion_actual}")

    return posiciones

def graficar_caminata(posiciones):
    """
    Grafica la trayectoria de la rana y muestra estadísticas de la caminata.

    Args:
        posiciones (list): Lista de posiciones de la rana en cada paso.
    """
    # Crear array de pasos para el eje x
    pasos = list(range(len(posiciones)))

    # Configurar la figura con tamaño apropiado
    plt.figure(figsize=(12, 6))

    # Graficar la trayectoria con línea y marcadores
    plt.plot(pasos, posiciones, 'b-o',     # Azul con círculos
             linewidth=2,                   # Línea gruesa
             markersize=4)                 # Marcadores medianos

    # Agregar línea de referencia en y=0
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Posición inicial')

    # Configurar etiquetas y título
    plt.xlabel('Número de Pasos')
    plt.ylabel('Posición de la Rana')
    plt.title('Caminata Aleatoria de una Rana')
    plt.grid(True, alpha=0.3)  # Grid sutil
    plt.legend()

    # Agregar anotaciones para posiciones clave
    plt.annotate(f'Inicio\nPos: {posiciones[0]}',
                 xy=(0, posiciones[0]),                    # Punto a anotar
                 xytext=(5, posiciones[0]+0.5),           # Posición del texto
                 arrowprops=dict(arrowstyle='->', color='green'))

    plt.annotate(f'Final\nPos: {posiciones[-1]}',
                 xy=(len(posiciones)-1, posiciones[-1]),
                 xytext=(len(posiciones)-6, posiciones[-1]+0.5),
                 arrowprops=dict(arrowstyle='->', color='red'))

    # Ajustar espacios y mostrar
    plt.tight_layout()
    plt.show()

    # Calcular y mostrar estadísticas de la caminata
    desplazamiento_final = posiciones[-1] - posiciones[0]
    distancia_maxima = max(posiciones) - min(posiciones)

    print(f"\nESTADÍSTICAS DE LA CAMINATA:")
    print(f"  Posición inicial: {posiciones[0]}")
    print(f"  Posición final: {posiciones[-1]}")
    print(f"  Rango de posiciones: [{min(posiciones)}, {max(posiciones)}]")
    print(f"  Distancia total recorrida: {len(posiciones)-1} pasos")

def main():
    """
    Función principal que controla el flujo del programa.
    Muestra el menú principal y maneja la navegación entre opciones.
    """
    # Bucle principal del programa
    while True:
        # Mostrar menú principal con emojis para mejor UX
        print(f"\nMENÚ PRINCIPAL")
        print(f"{'='*30}")
        print("1. Nueva simulación")
        print("2. Ver/gestionar histórico")
        print("3. Salir")

        # Obtener y procesar selección del usuario
        opcion = input("\nSeleccione una opción (1-3): ").strip()

        if opcion == "1":
            ejecutar_simulacion()  # Ejecutar simulación completa
        elif opcion == "2":
            menu_historico()       # Acceder al menú de histórico
        elif opcion == "3":
            print("¡Hasta luego!")
            break  # Salir del programa
        else:
            print("Opción inválida. Por favor, seleccione entre 1 y 3.")

def ejecutar_simulacion():
    """
    Ejecuta una simulación completa de caminata aleatoria.
    Incluye generación de números, pruebas estadísticas, simulación y visualización.
    """
    # Iniciar medición de tiempo de ejecución
    tiempo_inicio = time.time()

    # PASO 1: Obtener parámetros del generador
    x_o, k, c, g, n = obtener_parametros()

    # PASO 2: Generar números pseudoaleatorios
    print(f"\nGenerando {n} números pseudoaleatorios...")
    df = generar(x_o, k, c, g, n)  # Llamar al generador personalizado
    numeros = df['Ri'].tolist()     # Extraer columna de números aleatorios
    print(f"Números generados exitosamente")
    print(f"Primeros 5 números: {numeros[:5]}")

    # PASO 3: Configurar pruebas estadísticas
    pruebas, alpha = configurar_pruebas()

    # PASO 4: Ejecutar pruebas estadísticas (si se seleccionaron)
    if any(pruebas.values()):  # Verificar si hay al menos una prueba habilitada
        print(f"\nEjecutando pruebas estadísticas...")
        resultados = ejecutar_pruebas(numeros, pruebas, alpha)

        # Mostrar resultados y verificar si todas pasaron
        todas_pasaron = mostrar_resultados_pruebas(resultados)

        # Advertir al usuario si las pruebas fallaron
        if not todas_pasaron:
            print("\nADVERTENCIA: No todos los números pasaron las pruebas estadísticas")
            continuar = input("¿Desea continuar con la simulación de todos modos? (s/n): ")
            if not continuar.lower().startswith('s'):
                print("Simulación cancelada. Intente con otros parámetros.")
                return
    else:
        # Caso donde no se ejecutaron pruebas
        print("No se ejecutaron pruebas estadísticas")
        continuar = input("¿Desea continuar sin pruebas? (s/n): ")
        if not continuar.lower().startswith('s'):
            return

    # PASO 5: Configurar parámetros de la simulación
    print(f"\nIniciando simulación de caminata aleatoria...")
    posicion_inicial = int(input("Posición inicial de la rana (0): ") or "0")

    # Obtener número de pasos deseado
    num_pasos = obtener_numero_pasos(len(numeros))

    # PASO 6: Ejecutar la simulación de caminata
    posiciones = simular_caminata(numeros, posicion_inicial, num_pasos)

    # PASO 7: Generar visualización
    print(f"\nGenerando gráfica...")
    graficar_caminata(posiciones)

    # PASO 8: Guardar resultado en histórico
    agregar_posicion_final_al_historico(posiciones[-1])

    # PASO 9: Mostrar información final
    tiempo_fin = time.time()
    tiempo_total = tiempo_fin - tiempo_inicio
    print(f"\nTiempo total de ejecución: {tiempo_total:.3f} segundos")
    print(f"Simulación completada exitosamente!")

if __name__ == "__main__":
    try:
        main()  # Ejecutar programa principal
    except KeyboardInterrupt:
        print("\n\nSimulación interrumpida por el usuario")
    except Exception as e:
        print(f"\nError inesperado: {e}")
