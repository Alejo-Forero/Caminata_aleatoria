from prueba_de_medias import prueba_de_medias
from prueba_de_varianza import prueba_de_varianza
from prueba_chi2_2 import prueba_chi_cuadrado
from ks import kolmogorov_smirnov_test
from poker import poker_test_json
from rachas import prueba_rachas

PRUEBAS_DISPONIBLES = {
    "medias": prueba_de_medias,
    "varianza": prueba_de_varianza,
    "chi": prueba_chi_cuadrado,
    "kolmogorov": kolmogorov_smirnov_test,
    "poker": poker_test_json,
    "rachas": prueba_rachas
}

def ejecutar_pruebas(datos, pruebas, alpha):
    resultados = {}
    for nombre, info in pruebas.items():
        if nombre == "kolmogorov" and info != False and nombre in PRUEBAS_DISPONIBLES:
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, k=info.get("k") , alpha=alpha)
        elif nombre == "chi" and info != False and nombre in PRUEBAS_DISPONIBLES:
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, k=info.get("k"), alpha=alpha) 
        elif info and nombre in PRUEBAS_DISPONIBLES:
            resultados[nombre] = PRUEBAS_DISPONIBLES[nombre](datos, alpha=alpha)
    return resultados
