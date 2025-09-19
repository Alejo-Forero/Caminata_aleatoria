import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

# Parámetros de tu muestra
n = 50
gl = n - 1
varianza_muestral = 0.07160432

# Valores críticos de chi-cuadrado (previamente calculados)
chi2_inf = 31.5549165
chi2_sup = 70.2224136

# Intervalo de confianza para la varianza
Li = 0.11723274
Ls = 0.05267933

# Distribución chi-cuadrado
x = np.linspace(10, 90, 500)
y = stats.chi2.pdf(x, gl)

# Crear subplots (2 filas)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10,8), sharex=False, gridspec_kw={"height_ratios":[3,1]})

# --- Gráfico Chi-cuadrado ---
ax1.plot(x, y, label=f'Distribución Chi-cuadrado (gl={gl})')
ax1.fill_between(x, 0, y, where=(x>=chi2_inf)&(x<=chi2_sup), color="lightblue", alpha=0.5, label="Región de aceptación")
ax1.axvline(chi2_inf, color="green", linestyle="--", label="Límite inferior crítico")
ax1.axvline(chi2_sup, color="green", linestyle="--", label="Límite superior crítico")

ax1.set_title("Prueba de Varianza con Chi-Cuadrado y su Intervalo")
ax1.set_ylabel("Densidad de probabilidad")
ax1.legend()
ax1.grid(True)

# --- Intervalo de confianza para la varianza ---
ax2.hlines(1, Ls, Li, colors="blue", lw=4, label="Intervalo de confianza 95%")
ax2.plot(varianza_muestral, 1, "ro", label="Varianza muestral")

ax2.set_xlabel("Varianza")
ax2.set_yticks([])
ax2.legend()
ax2.grid(True, axis="x")

plt.tight_layout()
plt.show()
