import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
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

class CaminataAleatoria3D:

    def __init__(self):
        self.direcciones = {
            'Norte': (0, 1, 0),    # ↑ (Y+)
            'Sur': (0, -1, 0),     # ↓ (Y-)
            'Este': (1, 0, 0),     # → (X+)
            'Oeste': (-1, 0, 0),   # ← (X-)
            'Arriba': (0, 0, 1),   # ⬆ (Z+)
            'Abajo': (0, 0, -1)    # ⬇ (Z-)
        }
        self.nombres_direcciones = ['Norte', 'Sur', 'Este', 'Oeste', 'Arriba', 'Abajo']
        self.simbolos_direcciones = ['↑', '↓', '→', '←', '⬆', '⬇']

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
        print("SIMULADOR DE CAMINATA ALEATORIA 3D")
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
                    print(f"Error: El número de pasos debe estar entre 1 y {max_pasos}")
            except ValueError:
                print("Error: Ingrese un número entero válido")

    def determinar_direccion(self, numero_aleatorio):
        """
        Determina la dirección de movimiento basada en el número aleatorio
        Divide el rango [0,1) en 6 partes iguales para las 6 direcciones
        """
        if 0.0000 <= numero_aleatorio < 0.1667:  # ~1/6
            return 'Norte', self.direcciones['Norte'], '↑'
        elif 0.1667 <= numero_aleatorio < 0.3333:  # ~2/6
            return 'Sur', self.direcciones['Sur'], '↓'
        elif 0.3333 <= numero_aleatorio < 0.5000:  # ~3/6
            return 'Este', self.direcciones['Este'], '→'
        elif 0.5000 <= numero_aleatorio < 0.6667:  # ~4/6
            return 'Oeste', self.direcciones['Oeste'], '←'
        elif 0.6667 <= numero_aleatorio < 0.8333:  # ~5/6
            return 'Arriba', self.direcciones['Arriba'], '⬆'
        else:  # 0.8333 <= numero_aleatorio < 1.0000  # ~6/6
            return 'Abajo', self.direcciones['Abajo'], '⬇'

    def simular_caminata_3d(self, numeros_aleatorios, posicion_inicial_x=0, posicion_inicial_y=0, posicion_inicial_z=0, num_pasos=None):
        """Simula la caminata aleatoria de la rana en 3D"""
        if num_pasos is None:
            num_pasos = len(numeros_aleatorios)

        # Usar solo los primeros num_pasos números
        numeros_a_usar = numeros_aleatorios[:num_pasos]

        print(f"\n=== SIMULACIÓN DE CAMINATA ALEATORIA 3D ===")
        print(f"Posición inicial: ({posicion_inicial_x}, {posicion_inicial_y}, {posicion_inicial_z})")
        print(f"Direcciones posibles: Norte(↑), Sur(↓), Este(→), Oeste(←), Arriba(⬆), Abajo(⬇)")
        print(f"Probabilidad por dirección: ~16.67% cada una")
        print(f"Número de pasos a simular: {num_pasos}")
        print(f"Números disponibles: {len(numeros_aleatorios)}")

        # Listas para almacenar las posiciones
        posiciones_x = [posicion_inicial_x]
        posiciones_y = [posicion_inicial_y]
        posiciones_z = [posicion_inicial_z]

        # Posición actual
        x_actual = posicion_inicial_x
        y_actual = posicion_inicial_y
        z_actual = posicion_inicial_z

        # Estadísticas de movimiento
        conteo_direcciones = {'Norte': 0, 'Sur': 0, 'Este': 0, 'Oeste': 0, 'Arriba': 0, 'Abajo': 0}

        print("\nPasos de la rana:")
        print("Paso | Número   | Dirección | Mov | Posición (X, Y, Z)")
        print("-" * 55)

        for i, numero in enumerate(numeros_a_usar):
            direccion_nombre, (dx, dy, dz), simbolo = self.determinar_direccion(numero)

            # Actualizar posición
            x_actual += dx
            y_actual += dy
            z_actual += dz

            # Guardar nueva posición
            posiciones_x.append(x_actual)
            posiciones_y.append(y_actual)
            posiciones_z.append(z_actual)

            # Contar dirección
            conteo_direcciones[direccion_nombre] += 1

            print(f"{i+1:4d} | {numero:.5f} | {direccion_nombre:9s} | {simbolo:3s} | ({x_actual:3d}, {y_actual:3d}, {z_actual:3d})")

        return posiciones_x, posiciones_y, posiciones_z, conteo_direcciones

    def graficar_caminata_3d(self, posiciones_x, posiciones_y, posiciones_z, conteo_direcciones):
        """Grafica la trayectoria de la rana en 3D"""
        fig = plt.figure(figsize=(16, 6))

        # Gráfico 1: Trayectoria 3D
        ax1 = fig.add_subplot(121, projection='3d')

        # Línea de trayectoria
        ax1.plot(posiciones_x, posiciones_y, posiciones_z, 'b-', linewidth=2, alpha=0.7)

        # Puntos coloreados por tiempo
        scatter = ax1.scatter(posiciones_x, posiciones_y, posiciones_z,
                              c=range(len(posiciones_x)), cmap='viridis',
                              s=30, alpha=0.8, edgecolors='black', linewidth=0.5)

        # Marcar inicio y fin
        ax1.scatter(posiciones_x[0], posiciones_y[0], posiciones_z[0],
                    c='green', s=200, marker='s', label='Inicio',
                    edgecolors='black', linewidth=2)
        ax1.scatter(posiciones_x[-1], posiciones_y[-1], posiciones_z[-1],
                    c='red', s=200, marker='X', label='Final',
                    edgecolors='black', linewidth=2)

        # Planos de referencia en el origen
        max_range = max(max(posiciones_x) - min(posiciones_x),
                        max(posiciones_y) - min(posiciones_y),
                        max(posiciones_z) - min(posiciones_z))

        # Líneas de referencia
        ax1.plot([0, 0], [0, 0], [-max_range//2, max_range//2], 'k--', alpha=0.3)
        ax1.plot([0, 0], [-max_range//2, max_range//2], [0, 0], 'k--', alpha=0.3)
        ax1.plot([-max_range//2, max_range//2], [0, 0], [0, 0], 'k--', alpha=0.3)

        ax1.set_xlabel('Posición X')
        ax1.set_ylabel('Posición Y')
        ax1.set_zlabel('Posición Z')
        ax1.set_title('Caminata Aleatoria 3D de una Rana')
        ax1.legend()

        # Barra de color
        plt.colorbar(scatter, ax=ax1, label='Paso temporal', shrink=0.8)

        # Gráfico 2: Distribución de direcciones
        ax2 = fig.add_subplot(122)

        direcciones = list(conteo_direcciones.keys())
        conteos = list(conteo_direcciones.values())
        colores = ['lightblue', 'lightcoral', 'lightgreen', 'lightyellow', 'lightpink', 'lightgray']
        simbolos = ['↑', '↓', '→', '←', '⬆', '⬇']

        barras = ax2.bar(direcciones, conteos, color=colores, edgecolor='black', linewidth=1)

        # Agregar símbolos y valores en las barras
        for i, (barra, simbolo, valor) in enumerate(zip(barras, simbolos, conteos)):
            height = barra.get_height()
            ax2.text(barra.get_x() + barra.get_width()/2., height + 0.1,
                     f'{simbolo}\n{valor}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax2.set_ylabel('Número de Movimientos')
        ax2.set_title('Distribución de Direcciones 3D')
        ax2.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)

        # Línea de referencia para distribución uniforme
        if sum(conteos) > 0:
            promedio = sum(conteos) / 6
            ax2.axhline(y=promedio, color='red', linestyle='--',
                        label=f'Distribución uniforme ({promedio:.1f})', alpha=0.7)
            ax2.legend()

        plt.tight_layout()
        plt.show()

        # Crear gráficos adicionales de proyecciones
        self.graficar_proyecciones_3d(posiciones_x, posiciones_y, posiciones_z)

        # Estadísticas de la caminata
        self.mostrar_estadisticas_3d(posiciones_x, posiciones_y, posiciones_z, conteo_direcciones)

    def graficar_proyecciones_3d(self, posiciones_x, posiciones_y, posiciones_z):
        """Grafica las proyecciones de la caminata 3D en los planos XY, XZ, YZ"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

        # Proyección XY (vista desde arriba)
        ax1.plot(posiciones_x, posiciones_y, 'b-', linewidth=2, alpha=0.7)
        ax1.scatter(posiciones_x, posiciones_y, c=range(len(posiciones_x)),
                    cmap='viridis', s=20, alpha=0.8)
        ax1.scatter(posiciones_x[0], posiciones_y[0], c='green', s=100, marker='s', label='Inicio')
        ax1.scatter(posiciones_x[-1], posiciones_y[-1], c='red', s=100, marker='X', label='Final')
        ax1.set_xlabel('Posición X')
        ax1.set_ylabel('Posición Y')
        ax1.set_title('Proyección XY (Vista desde arriba)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_aspect('equal', adjustable='box')

        # Proyección XZ (vista desde el lado Y)
        ax2.plot(posiciones_x, posiciones_z, 'g-', linewidth=2, alpha=0.7)
        ax2.scatter(posiciones_x, posiciones_z, c=range(len(posiciones_x)),
                    cmap='viridis', s=20, alpha=0.8)
        ax2.scatter(posiciones_x[0], posiciones_z[0], c='green', s=100, marker='s', label='Inicio')
        ax2.scatter(posiciones_x[-1], posiciones_z[-1], c='red', s=100, marker='X', label='Final')
        ax2.set_xlabel('Posición X')
        ax2.set_ylabel('Posición Z')
        ax2.set_title('Proyección XZ (Vista desde el lado)')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_aspect('equal', adjustable='box')

        # Proyección YZ (vista desde el lado X)
        ax3.plot(posiciones_y, posiciones_z, 'r-', linewidth=2, alpha=0.7)
        ax3.scatter(posiciones_y, posiciones_z, c=range(len(posiciones_y)),
                    cmap='viridis', s=20, alpha=0.8)
        ax3.scatter(posiciones_y[0], posiciones_z[0], c='green', s=100, marker='s', label='Inicio')
        ax3.scatter(posiciones_y[-1], posiciones_z[-1], c='red', s=100, marker='X', label='Final')
        ax3.set_xlabel('Posición Y')
        ax3.set_ylabel('Posición Z')
        ax3.set_title('Proyección YZ (Vista frontal)')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        ax3.set_aspect('equal', adjustable='box')

        # Gráfico de evolución temporal de coordenadas
        pasos = range(len(posiciones_x))
        ax4.plot(pasos, posiciones_x, 'r-', label='X', linewidth=2)
        ax4.plot(pasos, posiciones_y, 'g-', label='Y', linewidth=2)
        ax4.plot(pasos, posiciones_z, 'b-', label='Z', linewidth=2)
        ax4.set_xlabel('Número de Paso')
        ax4.set_ylabel('Posición')
        ax4.set_title('Evolución Temporal de Coordenadas')
        ax4.grid(True, alpha=0.3)
        ax4.legend()

        plt.tight_layout()
        plt.show()

    def mostrar_estadisticas_3d(self, posiciones_x, posiciones_y, posiciones_z, conteo_direcciones):
        """Muestra estadísticas detalladas de la caminata 3D"""
        print(f"\n📈 ESTADÍSTICAS DE LA CAMINATA 3D:")

        # Posiciones
        print(f"  Posición inicial: ({posiciones_x[0]}, {posiciones_y[0]}, {posiciones_z[0]})")
        print(f"  Posición final: ({posiciones_x[-1]}, {posiciones_y[-1]}, {posiciones_z[-1]})")

        # Desplazamientos
        dx_total = posiciones_x[-1] - posiciones_x[0]
        dy_total = posiciones_y[-1] - posiciones_y[0]
        dz_total = posiciones_z[-1] - posiciones_z[0]
        distancia_euclidiana = np.sqrt(dx_total**2 + dy_total**2 + dz_total**2)

        print(f"  Desplazamiento neto: ({dx_total:+d}, {dy_total:+d}, {dz_total:+d})")
        print(f"  Distancia euclidiana del origen: {distancia_euclidiana:.2f}")

        # Rangos
        rango_x = (min(posiciones_x), max(posiciones_x))
        rango_y = (min(posiciones_y), max(posiciones_y))
        rango_z = (min(posiciones_z), max(posiciones_z))
        volumen_explorado = (rango_x[1] - rango_x[0] + 1) * (rango_y[1] - rango_y[0] + 1) * (rango_z[1] - rango_z[0] + 1)

        print(f"  Rango X: [{rango_x[0]}, {rango_x[1]}] (amplitud: {rango_x[1] - rango_x[0] + 1})")
        print(f"  Rango Y: [{rango_y[0]}, {rango_y[1]}] (amplitud: {rango_y[1] - rango_y[0] + 1})")
        print(f"  Rango Z: [{rango_z[0]}, {rango_z[1]}] (amplitud: {rango_z[1] - rango_z[0] + 1})")
        print(f"  Volumen explorado: {volumen_explorado} unidades cúbicas")

        # Distancias en proyecciones
        dist_xy = np.sqrt(dx_total**2 + dy_total**2)
        dist_xz = np.sqrt(dx_total**2 + dz_total**2)
        dist_yz = np.sqrt(dy_total**2 + dz_total**2)

        print(f"\nDISTANCIAS EN PROYECCIONES:")
        print(f"  Distancia XY: {dist_xy:.2f}")
        print(f"  Distancia XZ: {dist_xz:.2f}")
        print(f"  Distancia YZ: {dist_yz:.2f}")

        # Distribución de direcciones
        total_pasos = sum(conteo_direcciones.values())
        print(f"\nDISTRIBUCIÓN DE DIRECCIONES 3D:")
        simbolos_dict = {'Norte': '↑', 'Sur': '↓', 'Este': '→', 'Oeste': '←', 'Arriba': '⬆', 'Abajo': '⬇'}

        for direccion, count in conteo_direcciones.items():
            porcentaje = (count / total_pasos) * 100 if total_pasos > 0 else 0
            simbolo = simbolos_dict[direccion]
            print(f"  {direccion:6s} {simbolo}: {count:3d} pasos ({porcentaje:5.1f}%)")

        print(f"  Total de pasos: {total_pasos}")

        # Análisis de simetría
        print(f"\n⚖ANÁLISIS DE SIMETRÍA:")
        mov_horizontal = conteo_direcciones['Norte'] + conteo_direcciones['Sur'] + conteo_direcciones['Este'] + conteo_direcciones['Oeste']
        mov_vertical = conteo_direcciones['Arriba'] + conteo_direcciones['Abajo']

        if total_pasos > 0:
            print(f"  Movimientos horizontales (N,S,E,O): {mov_horizontal} ({(mov_horizontal/total_pasos)*100:.1f}%)")
            print(f"  Movimientos verticales (⬆,⬇): {mov_vertical} ({(mov_vertical/total_pasos)*100:.1f}%)")

    def ejecutar_simulacion(self):
        """Función principal que ejecuta toda la simulación"""
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

                # Mostrar resultados
                todas_pasaron = self.mostrar_resultados_pruebas(resultados)

                if not todas_pasaron:
                    print("\n⚠ADVERTENCIA: No todos los números pasaron las pruebas estadísticas")
                    continuar = input("¿Desea continuar con la simulación de todos modos? (s/n): ")
                    if not continuar.lower().startswith('s'):
                        print("Simulación cancelada. Intente con otros parámetros.")
                        return
            else:
                print("No se ejecutaron pruebas estadísticas")
                continuar = input("¿Desea continuar sin pruebas? (s/n): ")
                if not continuar.lower().startswith('s'):
                    return

            print(f"\nIniciando simulación de caminata aleatoria 3D...")
            posicion_inicial_x = int(input("Posición inicial X (0): ") or "0")
            posicion_inicial_y = int(input("Posición inicial Y (0): ") or "0")
            posicion_inicial_z = int(input("Posición inicial Z (0): ") or "0")

            num_pasos = self.obtener_numero_pasos(len(numeros))

            posiciones_x, posiciones_y, posiciones_z, conteo_direcciones = self.simular_caminata_3d(
                numeros, posicion_inicial_x, posicion_inicial_y, posicion_inicial_z, num_pasos
            )

            print(f"\nGenerando gráficas...")
            self.graficar_caminata_3d(posiciones_x, posiciones_y, posiciones_z, conteo_direcciones)

            print(f"\nSimulación 3D completada exitosamente!")

        except KeyboardInterrupt:
            print("\n\n⚠Simulación interrumpida por el usuario")
        except Exception as e:
            print(f"\nError inesperado: {e}")

def main():
    simulador = CaminataAleatoria3D()
    simulador.ejecutar_simulacion()

if __name__ == "__main__":
    main()