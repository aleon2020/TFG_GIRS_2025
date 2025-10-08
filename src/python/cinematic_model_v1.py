# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.

import numpy as np
import matplotlib.pyplot as plt

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# python3 cinematic_model_v1.py

# PARÁMETROS
largo_plano = 100
alto_plano = 100
largo_efector = 10
alto_efector = 10
radio_rueda = 5

# SOLICITUD DE LAS COORDENADAS DEL EFECTOR FINAL
print("\nCOORDENADAS DEL EFECTOR FINAL")
x_efector = float(input('Coordenada x del efector final: '))
y_efector = float(input('Coordenada y del efector final: '))
print()

# VERIFICACIÓN DE LÍMITES

error = False

if x_efector >= (largo_plano - (largo_efector / 2)):
    print("FUERA DEL LÍMITE en x =", x_efector)
    error = True
elif x_efector <= (largo_efector / 2):
    print("FUERA DEL LÍMITE en x =", x_efector)
    error = True

if y_efector >= (alto_plano - (alto_efector / 2)):
    print("FUERA DEL LÍMITE en y =", y_efector)
    error = True
elif y_efector <= (alto_efector / 2):
    print("FUERA DEL LÍMITE en y =", y_efector)
    error = True

if error:
    exit()

# PLANO
fig, ax = plt.subplots(figsize=(20, 16))
ax.set_xlim([-largo_plano * 0.25, largo_plano * 1.25])
ax.set_ylim([-alto_plano * 0.5, alto_plano * 1.25])
ax.set_xlabel('Eje X (centímetros)')
ax.set_ylabel('Eje Y (centímetros)')
ax.set_title('Robot por cables para el control de un efector final')

# ESTRUCTURA
ax.plot([0, 0], [alto_plano, -(alto_plano / 2)], 'k', linewidth=5)
ax.plot([largo_plano, largo_plano], [alto_plano, -(alto_plano / 2)], 'k', linewidth=5)
ax.plot([0, largo_plano], [alto_plano, alto_plano], 'k', linewidth=5)
ax.plot([0, largo_plano], [0, 0], 'k', linewidth=5)
ax.plot([-5, 5], [-(alto_plano / 2), -(alto_plano / 2)], 'k', linewidth=5)
ax.plot([largo_plano - 5, largo_plano + 5], [-(alto_plano / 2), -(alto_plano / 2)], 'k', linewidth=5)

# EFECTOR FINAL

# Esquina superior izquierda (x1, y1)
x1 = x_efector - (largo_efector / 2)
y1 = y_efector + (alto_efector / 2)

# Esquina superior derecha (x2, y2)
x2 = x_efector + (largo_efector / 2)
y2 = y_efector + (alto_efector / 2)

# Esquina inferior izquierda (x3, y3)
x3 = x_efector - (largo_efector / 2)
y3 = y_efector - (alto_efector / 2)

# Esquina inferior derecha (x4, y4)
x4 = x_efector + (largo_efector / 2)
y4 = y_efector - (alto_efector / 2)

# CABLES

# Cable esquina superior izquierda M1 = (M1x, M1y)
M1x = 0
M1y = alto_plano
ax.plot([M1x, x1], [M1y, y1], 'r', linewidth=2)

# Cable esquina superior derecha M2 = (M2x, M2y)
M2x = largo_plano
M2y = alto_plano
ax.plot([M2x, x2], [M2y, y2], 'r', linewidth=2)

# REPRESENTACIÓN EFECTOR FINAL
xe = [x3, x4, x2, x1, x3]
ye = [y3, y4, y2, y1, y3]
ax.plot(xe, ye, 'black', linewidth=2)
ax.plot(x_efector, y_efector, 'ko', markersize=2, markerfacecolor='black')

# REPRESENTACIÓN RUEDAS
ax.plot(0, alto_plano, 'ko', markersize=radio_rueda, markerfacecolor='black')
ax.plot(0, alto_plano, 'wo', markersize=radio_rueda / 2, markerfacecolor='black')
ax.plot(largo_plano, alto_plano, 'ko', markersize=radio_rueda, markerfacecolor='black')
ax.plot(largo_plano, alto_plano, 'wo', markersize=radio_rueda / 2, markerfacecolor='black')

# LONGITUDES DE LOS CABLES
L1 = np.sqrt((x1 - M1x) ** 2 + (y1 - M1y) ** 2)
L2 = np.sqrt((x2 - M2x) ** 2 + (y2 - M2y) ** 2)
print("Longitud del cable L1 =", L1, "cm")
print("Longitud del cable L2 =", L2, "cm")

# ÁNGULOS
q1 = -np.degrees(np.arctan((x1 - M1x) / (y1 - M1y)))
q2 = np.degrees(np.arctan((x2 - M2x) / (y2 - M2y)))
print("Ángulo del cable L1 (q1) =", q1, "°")
print("Ángulo del cable L2 (q2) =", q2, "°")

plt.show()