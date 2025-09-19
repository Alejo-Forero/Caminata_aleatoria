import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import os


from pruebas.Generador import generar

from pruebas.prueba_de_medias import prueba_de_medias
from pruebas.prueba_de_varianza import prueba_de_varianza
from pruebas.prueba_chi2_2 import prueba_chi_cuadrado
from pruebas.ks import kolmogorov_smirnov_test
from pruebas.poker import poker_test_json
from pruebas.rachas import prueba_rachas

class CaminataAleatoria2D:

    def __init__(self):
        """Inicializa la clase de caminata 2D"""
        self.direcciones = {
            'Norte': (0, 1),   # ↑
            'Sur': (0, -1),    # ↓
            'Este': (1, 0),    # →
            'Oeste': (-1, 0)   # ←
        }
        self.nombres_direcciones = ['Norte', 'Este', 'Sur', 'Oeste']
        self.simbolos_direcciones = ['↑', '→', '↓', '←']

        # Diccionario de pruebas disponibles
        self.PRUEBAS_DISPONIBLES = {
            "medias": prueba_de_medias,
            "varianza": prueba_de_varianza,
            "chi": prueba_chi_cuadrado,
            "kolmogorov": kolmogorov_smirnov_test,
            "poker": poker_test_json,
            "rachas": prueba_rachas
        }

    def obtener_parametros_generacion(self):
        """Obtiene los parámetros del usuario para la generación de números"""
        print("SIMULADOR DE CAMINATA ALEATORIA 2D")
        print("=" * 50)
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
            return self.obtener_parametros_generacion()

    def configurar_pruebas(self):
        """Configura qué pruebas estadísticas ejecutar"""
        print("\n=== CONFIGURACIÓN DE PRUEBAS ESTADÍSTICAS ===")
        print("¿Qué pruebas desea ejecutar? (s/n)")

        pruebas = {}

        # Pruebas básicas
        pruebas["medias"] = input("Prueba de Medias (s/n): ").lower().startswith('s')
        pruebas["varianza"] = input("Prueba de Varianza (s/n): ").lower().startswith('s')
        pruebas["rachas"] = input("Prueba de Rachas (s/n): ").lower().startswith('s')
        pruebas["poker"] = input("Prueba de Póker (s/n): ").lower().startswith('s')

        # Pruebas con parámetros
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

        # Nivel de significancia
        alpha = float(input("Nivel de significancia (alpha, ej: 0.05): ") or "0.05")

        return pruebas, alpha

    def ejecutar_pruebas(self, datos, pruebas, alpha):
        """Ejecuta las pruebas estadísticas seleccionadas"""
        resultados = {}
        for nombre, info in pruebas.items():
            if nombre == "kolmogorov" and info != False and nombre in self.PRUEBAS_DISPONIBLES:
                resultados[nombre] = self.PRUEBAS_DISPONIBLES[nombre](datos, k=info.get("k"), alpha=alpha)
            elif nombre == "chi" and info != False and nombre in self.PRUEBAS_DISPONIBLES:
                resultados[nombre] = self.PRUEBAS_DISPONIBLES[nombre](datos, k=info.get("k"), alpha=alpha)
            elif info and nombre in self.PRUEBAS_DISPONIBLES:
                resultados[nombre] = self.PRUEBAS_DISPONIBLES[nombre](datos, alpha=alpha)
        return resultados

    def mostrar_resultados_pruebas(self, resultados):
        """Muestra los resultados de las pruebas estadísticas"""
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

    def obtener_numero_pasos(self, max_pasos):
        """Obtiene el número de pasos que el usuario quiere simular"""
        while True:
            try:
                pasos = int(input(f"¿Cuántos pasos quiere que dé la rana? (máximo {max_pasos}): "))
                if 1 <= pasos <= max_pasos:
                    return pasos
                else:
                    print(f"❌ Error: El número de pasos debe estar entre 1 y {max_pasos}")
            except ValueError:
                print("❌ Error: Ingrese un número entero válido")

    def determinar_direccion(self, numero_aleatorio):

        if 0.00 <= numero_aleatorio < 0.25:
            return 'Norte', self.direcciones['Norte'], '↑'
        elif 0.25 <= numero_aleatorio < 0.50:
            return 'Este', self.direcciones['Este'], '→'
        elif 0.50 <= numero_aleatorio < 0.75:
            return 'Sur', self.direcciones['Sur'], '↓'
        else:  # 0.75 <= numero_aleatorio < 1.00
            return 'Oeste', self.direcciones['Oeste'], '←'

    def simular_caminata_2d(self, numeros_aleatorios, posicion_inicial_x=0, posicion_inicial_y=0, num_pasos=None):
        """Simula la caminata aleatoria de la rana en 2D"""
        if num_pasos is None:
            num_pasos = len(numeros_aleatorios)

        # Usar solo los primeros num_pasos números
        numeros_a_usar = numeros_aleatorios[:num_pasos]

        print(f"\n=== SIMULACIÓN DE CAMINATA ALEATORIA 2D ===")
        print(f"Posición inicial: ({posicion_inicial_x}, {posicion_inicial_y})")
        print(f"Direcciones posibles: Norte(↑), Este(→), Sur(↓), Oeste(←)")
        print(f"Probabilidad por dirección: 0.25 cada una")
        print(f"Número de pasos a simular: {num_pasos}")
        print(f"Números disponibles: {len(numeros_aleatorios)}")

        # Listas para almacenar las posiciones
        posiciones_x = [posicion_inicial_x]
        posiciones_y = [posicion_inicial_y]

        # Posición actual
        x_actual = posicion_inicial_x
        y_actual = posicion_inicial_y

        # Estadísticas de movimiento
        conteo_direcciones = {'Norte': 0, 'Este': 0, 'Sur': 0, 'Oeste': 0}

        print("\nPasos de la rana:")
        print("Paso | Número   | Dirección | Movimiento | Posición")
        print("-" * 50)

        for i, numero in enumerate(numeros_a_usar):
            direccion_nombre, (dx, dy), simbolo = self.determinar_direccion(numero)

            # Actualizar posición
            x_actual += dx
            y_actual += dy

            # Guardar nueva posición
            posiciones_x.append(x_actual)
            posiciones_y.append(y_actual)

            # Contar dirección
            conteo_direcciones[direccion_nombre] += 1

            print(f"{i+1:4d} | {numero:.5f} | {direccion_nombre:8s} | {simbolo:8s}   | ({x_actual:3d}, {y_actual:3d})")

        return posiciones_x, posiciones_y, conteo_direcciones

    def graficar_caminata_2d(self, posiciones_x, posiciones_y, conteo_direcciones):
        """Grafica la trayectoria de la rana en 2D"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Gráfico 1: Trayectoria de la caminata
        ax1.plot(posiciones_x, posiciones_y, 'b-', linewidth=2, alpha=0.7, label='Trayectoria')
        ax1.scatter(posiciones_x, posiciones_y, c=range(len(posiciones_x)),
                    cmap='viridis', s=30, alpha=0.8, edgecolors='black', linewidth=0.5)

        # Marcar inicio y fin
        ax1.scatter(posiciones_x[0], posiciones_y[0], c='green', s=150,
                    marker='s', label='Inicio', edgecolors='black', linewidth=2)
        ax1.scatter(posiciones_x[-1], posiciones_y[-1], c='red', s=150,
                    marker='X', label='Final', edgecolors='black', linewidth=2)

        # Líneas de referencia
        ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.5)

        ax1.set_xlabel('Posición X')
        ax1.set_ylabel('Posición Y')
        ax1.set_title('Caminata Aleatoria 2D de una Rana')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_aspect('equal', adjustable='box')

        # Gráfico 2: Distribución de direcciones
        direcciones = list(conteo_direcciones.keys())
        conteos = list(conteo_direcciones.values())
        colores = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
        simbolos = ['↑', '→', '↓', '←']

        barras = ax2.bar(direcciones, conteos, color=colores, edgecolor='black', linewidth=1)

        # Agregar símbolos y valores en las barras
        for i, (barra, simbolo, valor) in enumerate(zip(barras, simbolos, conteos)):
            height = barra.get_height()
            ax2.text(barra.get_x() + barra.get_width()/2., height + 0.1,
                     f'{simbolo}\n{valor}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax2.set_ylabel('Número de Movimientos')
        ax2.set_title('Distribución de Direcciones')
        ax2.grid(True, alpha=0.3, axis='y')

        # Línea de referencia para distribución uniforme
        if sum(conteos) > 0:
            promedio = sum(conteos) / 4
            ax2.axhline(y=promedio, color='red', linestyle='--',
                        label=f'Distribución uniforme ({promedio:.1f})', alpha=0.7)
            ax2.legend()

        plt.tight_layout()
        plt.show()

        # Estadísticas de la caminata
        self.mostrar_estadisticas_2d(posiciones_x, posiciones_y, conteo_direcciones)

    def mostrar_estadisticas_2d(self, posiciones_x, posiciones_y, conteo_direcciones):
        """Muestra estadísticas detalladas de la caminata 2D"""
        print(f"\nESTADÍSTICAS DE LA CAMINATA 2D:")

        # Posiciones
        print(f"  Posición inicial: ({posiciones_x[0]}, {posiciones_y[0]})")
        print(f"  Posición final: ({posiciones_x[-1]}, {posiciones_y[-1]})")

        # Desplazamientos
        dx_total = posiciones_x[-1] - posiciones_x[0]
        dy_total = posiciones_y[-1] - posiciones_y[0]
        distancia_euclidiana = np.sqrt(dx_total**2 + dy_total**2)

        print(f"  Desplazamiento neto: ({dx_total:+d}, {dy_total:+d})")
        print(f"  Distancia euclidiana del origen: {distancia_euclidiana:.2f}")

        # Rangos
        rango_x = (min(posiciones_x), max(posiciones_x))
        rango_y = (min(posiciones_y), max(posiciones_y))
        area_explorada = (rango_x[1] - rango_x[0] + 1) * (rango_y[1] - rango_y[0] + 1)

        print(f"  Rango X: [{rango_x[0]}, {rango_x[1]}] (amplitud: {rango_x[1] - rango_x[0] + 1})")
        print(f"  Rango Y: [{rango_y[0]}, {rango_y[1]}] (amplitud: {rango_y[1] - rango_y[0] + 1})")
        print(f"  Área explorada: {area_explorada} unidades cuadradas")

        # Distribución de direcciones
        total_pasos = sum(conteo_direcciones.values())
        print(f"\nDISTRIBUCIÓN DE DIRECCIONES:")
        for direccion, count in conteo_direcciones.items():
            porcentaje = (count / total_pasos) * 100 if total_pasos > 0 else 0
            simbolo = {'Norte': '↑', 'Este': '→', 'Sur': '↓', 'Oeste': '←'}[direccion]
            print(f"  {direccion} {simbolo}: {count:3d} pasos ({porcentaje:5.1f}%)")

        print(f"  Total de pasos: {total_pasos}")

    def ejecutar_simulacion(self):
        try:
            x_o, k, c, g, n = self.obtener_parametros_generacion()

            print(f"\nGenerando {n} números pseudoaleatorios...")
            df = generar(x_o, k, c, g, n)
            numeros = df['Ri'].tolist()
            print(f"Números generados exitosamente")
            print(f"Primeros 5 números: {numeros[:5]}")

            pruebas, alpha = self.configurar_pruebas()

            if any(pruebas.values()):
                print(f"\nEjecutando pruebas estadísticas...")
                resultados = self.ejecutar_pruebas(numeros, pruebas, alpha)

                todas_pasaron = self.mostrar_resultados_pruebas(resultados)

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

            print(f"\nIniciando simulación de caminata aleatoria 2D...")
            posicion_inicial_x = int(input("Posición inicial X (0): ") or "0")
            posicion_inicial_y = int(input("Posición inicial Y (0): ") or "0")

            num_pasos = self.obtener_numero_pasos(len(numeros))

            posiciones_x, posiciones_y, conteo_direcciones = self.simular_caminata_2d(
                numeros, posicion_inicial_x, posicion_inicial_y, num_pasos
            )

            print(f"\nGenerando gráficas...")
            self.graficar_caminata_2d(posiciones_x, posiciones_y, conteo_direcciones)

            print(f"\nSimulación 2D completada exitosamente!")

        except KeyboardInterrupt:
            print("\n\nSimulación interrumpida por el usuario")
        except Exception as e:
            print(f"\nError inesperado: {e}")

def main():
    simulador = CaminataAleatoria2D()
    simulador.ejecutar_simulacion()

if __name__ == "__main__":
    main()