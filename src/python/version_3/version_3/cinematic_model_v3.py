# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def main():

    # PARÁMETROS
    largo_plano = 100
    alto_plano = 100
    largo_efector = 10
    alto_efector = 10
    radio_rueda = 25

    # SOLICITUD DEL NÚMERO DE POSICIONES
    num_posiciones = int(input("\nNÚMERO DE POSICIONES (MÍNIMO 2, MÁXIMO 10): "))
    num_posiciones = max(2, min(10, num_posiciones))

    posiciones = []
    errores = {}

    # SOLICITUD DE LAS COORDENADAS DEL EFECTOR FINAL
    for i in range(num_posiciones):
        print(f"\nPOSICIÓN NÚMERO {i+1} DEL EFECTOR FINAL")
        x = float(input(f'Coordenada x de la posición número {i+1}: '))
        y = float(input(f'Coordenada y de la posición número {i+1}: '))
        posiciones.append((x, y))

    # VERIFICACIÓN DE LÍMITES

    def verificar_limites(x, y):
        errores = []
        if x >= (largo_plano - (largo_efector / 2)) or x <= (largo_efector / 2):
            errores.append(f"FUERA DEL LÍMITE en x = {x}")
        if y >= (alto_plano - (alto_efector / 2)) or y <= (alto_efector / 2):
            errores.append(f"FUERA DEL LÍMITE en y = {y}")
        return errores

    for i, (x, y) in enumerate(posiciones):
        errores_posicion = verificar_limites(x, y)
        if errores_posicion:
            errores[i+1] = errores_posicion

    if errores:
        for pos, errs in errores.items():
            print(f"\nERROR EN LA POSICIÓN NÚMERO {pos}")
            for err in errs:
                print(err)
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

    # REPRESENTACIÓN RUEDAS (fijas)
    ax.plot(0, alto_plano, 'ko', markersize=radio_rueda, markerfacecolor='black')
    ax.plot(0, alto_plano, 'wo', markersize=radio_rueda / 2, markerfacecolor='black')
    ax.plot(largo_plano, alto_plano, 'ko', markersize=radio_rueda, markerfacecolor='black')
    ax.plot(largo_plano, alto_plano, 'wo', markersize=radio_rueda / 2, markerfacecolor='black')

    # ACTUALIZACIÓN DE LA POSICIÓN DE LOS ELEMENTOS DESPLAZADOS
    efector, = ax.plot([], [], 'black', linewidth=2)
    centro_efector, = ax.plot([], [], 'ko', markersize=2, markerfacecolor='black')
    cable1, = ax.plot([], [], 'r', linewidth=2)
    cable2, = ax.plot([], [], 'r', linewidth=2)
    trayectoria, = ax.plot([], [], 'b--', linewidth=1, alpha=0.5)

    # ALMACENAMIENTO DE LOS PUNTOS DE LA TRAYECTORIA REALIZADA
    trayectoria_x = []
    trayectoria_y = []

    # EFECTOR FINAL
    def calcular_esquinas(x, y):

        # Esquina superior izquierda (x1, y1)
        x1 = x - (largo_efector / 2)
        y1 = y + (alto_efector / 2)

        # Esquina superior derecha (x2, y2)
        x2 = x + (largo_efector / 2)
        y2 = y + (alto_efector / 2)

        # Esquina inferior izquierda (x3, y3)
        x3 = x - (largo_efector / 2)
        y3 = y - (alto_efector / 2)

        # Esquina inferior derecha (x4, y4)
        x4 = x + (largo_efector / 2)
        y4 = y - (alto_efector / 2)
        
        return x1, y1, x2, y2, x3, y3, x4, y4

    # CABLES
    def calcular_cables(x, y):
        x1, y1, x2, y2, _, _, _, _ = calcular_esquinas(x, y)
        
        # Cable esquina superior izquierda M1 = (M1x, M1y)
        M1x = 0
        M1y = alto_plano

        # Cable esquina superior derecha M2 = (M2x, M2y)
        M2x = largo_plano
        M2y = alto_plano
        
        # LONGITUDES DE LOS CABLES
        L1 = np.sqrt((x1 - M1x) ** 2 + (y1 - M1y) ** 2)
        L2 = np.sqrt((x2 - M2x) ** 2 + (y2 - M2y) ** 2)
        
        # ÁNGULOS
        q1 = -np.degrees(np.arctan((x1 - M1x) / (y1 - M1y)))
        q2 = np.degrees(np.arctan((x2 - M2x) / (y2 - M2y)))
        
        return L1, L2, q1, q2

    # INICIALIZACIÓN DE DATOS DE LA ANIMACIÓN
    def init():
        efector.set_data([], [])
        centro_efector.set_data([], [])
        cable1.set_data([], [])
        cable2.set_data([], [])
        trayectoria.set_data([], [])
        return efector, centro_efector, cable1, cable2, trayectoria

    # ANIMACIÓN
    def animate(i):

        # FRAMES
        segmentos = num_posiciones - 1
        frames_por_segmento = 100 // segmentos
        segmento_actual = min(i // frames_por_segmento, segmentos - 1)
        progreso = (i % frames_por_segmento) / frames_por_segmento
        
        # POSICIÓN INICIAL Y FINAL DEL SEGMENTO ACTUAL
        x_inicio, y_inicio = posiciones[segmento_actual]
        x_fin, y_fin = posiciones[segmento_actual + 1]
        
        # CÁLCULO DE LA POSICIÓN ACTUAL
        x = x_inicio + (x_fin - x_inicio) * progreso
        y = y_inicio + (y_fin - y_inicio) * progreso
        
        # ESQUINAS EFECTOR FINAL
        x1, y1, x2, y2, x3, y3, x4, y4 = calcular_esquinas(x, y)
        
        # REPRESENTACIÓN EFECTOR FINAL
        xe = [x3, x4, x2, x1, x3]
        ye = [y3, y4, y2, y1, y3]
        efector.set_data(xe, ye)
        centro_efector.set_data(x, y)

        # CABLES
        
        # Cable esquina superior izquierda M1 = (M1x, M1y)
        M1x = 0
        M1y = alto_plano

        # Cable esquina superior derecha M2 = (M2x, M2y)
        M2x = largo_plano
        M2y = alto_plano

        # ACTUALIZACIÓN DE LA POSICIÓN DE LOS CABLES
        cable1.set_data([M1x, x1], [M1y, y1])
        cable2.set_data([M2x, x2], [M2y, y2])
        
        # ACTUALIZACIÓN DE LA TRAYECTORIA
        trayectoria_x.append(x)
        trayectoria_y.append(y)
        trayectoria.set_data(trayectoria_x, trayectoria_y)
        
        return efector, centro_efector, cable1, cable2, trayectoria

    # MOSTRAR DATOS DE CADA POSICIÓN
    for i, (x, y) in enumerate(posiciones):
        print(f"\nDATOS POSICIÓN NÚMERO {i+1}")
        L1, L2, q1, q2 = calcular_cables(x, y)
        print("Longitud del cable L1 =", L1, "cm")
        print("Longitud del cable L2 =", L2, "cm")
        print("Ángulo del cable L1 (q1) =", q1, "°")
        print("Ángulo del cable L2 (q2) =", q2, "°")

    # CREACIÓN DE LA ANIMACIÓN
    ani = FuncAnimation(fig, 
                        animate, 
                        frames=100, 
                        init_func=init,
                        blit=True, 
                        interval=50, 
                        repeat=False)

    plt.show()

if __name__ == "__main__":
    main()