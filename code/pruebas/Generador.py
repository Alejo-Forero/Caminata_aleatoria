import pandas as pd

def generar(x0: int, t: int, g: int, n: int, min_value: float = 0, max_value: float = 1):

    # Parámetros
    m = 2 ** g
    a = 8 * t + 3
    xi = x0

    # Resultados
    data = []

    for i in range(n):
        xi = (a * xi) % m
        ri = truncar(xi / (m - 1),5)   # Normalización
        data.append([i + 1, xi, ri])

    # Convertir en DataFrame
    df = pd.DataFrame(data, columns=["i", "Xi", "Ri"])
    return df

def truncar(n, decimales=0):
    factor = 10.0 ** decimales
    return int(n * factor) / factor

# # Ejemplo de uso
# if __name__ == "__main__":
#     tabla = generar(x0=5, t=3, g=16, n=50, min_value=0, max_value=100)
#     print(tabla)
