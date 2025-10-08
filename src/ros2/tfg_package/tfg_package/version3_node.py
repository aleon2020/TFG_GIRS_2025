# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.
import rclpy
from rclpy.node import Node
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from std_msgs.msg import Float64MultiArray
import sys

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# colcon build --symlink-install
# ros2 run tfg_package version3_node

class Version3Node(Node):

    # PARÁMETROS
    def __init__(self):
        super().__init__('version3_node')
        self.declare_parameters(
            namespace='',
            parameters=[
                ('largo_plano', 100),
                ('alto_plano', 100),
                ('largo_efector', 10),
                ('alto_efector', 10),
                ('radio_rueda', 5),
                ('max_posiciones', 10)
            ]
        )
        self.largo_plano = self.get_parameter('largo_plano').value
        self.alto_plano = self.get_parameter('alto_plano').value
        self.largo_efector = self.get_parameter('largo_efector').value
        self.alto_efector = self.get_parameter('alto_efector').value
        self.radio_rueda = self.get_parameter('radio_rueda').value
        self.max_posiciones = self.get_parameter('max_posiciones').value
        self.cable_publisher = self.create_publisher(Float64MultiArray, 'cable_parameters', 10)
        self.coordinates_publisher = self.create_publisher(Float64MultiArray, 'effector_coordinates', 10)
        self.pulley_publisher = self.create_publisher(Float64MultiArray, 'pulley_parameters', 10)
        self.solicitar_coordenadas()
        self.publicar_coordenadas()
        if not self.verificar_todas_posiciones():
            self.dibujar_estructura()
    
    # SOLICITUD DE LAS COORDENADAS DEL EFECTOR FINAL
    def solicitar_coordenadas(self):
        try:

            # SOLICITUD DEL NÚMERO DE POSICIONES
            print(f"\nNÚMERO DE POSICIONES (MÍNIMO 2, MÁXIMO {self.max_posiciones})")
            self.num_posiciones = int(input('Número de posiciones: '))
            self.num_posiciones = max(2, min(self.max_posiciones, self.num_posiciones))
            self.posiciones = []

            # SOLICITUD DE LAS COORDENADAS DEL EFECTOR FINAL
            for i in range(self.num_posiciones):
                print(f"\nPOSICIÓN NÚMERO {i+1} DEL EFECTOR FINAL")
                x = float(input(f'Coordenada x de la posición número {i+1}: '))
                y = float(input(f'Coordenada y de la posición número {i+1}: '))
                self.posiciones.append((x, y))

        except ValueError:
            self.get_logger().error("Coordenadas incorrectas / fuera de rango")
            sys.exit(1)
    
    # PUBLICACIÓN DE LAS COORDENADAS DEL EFECTOR FINAL
    def publicar_coordenadas(self):
        coordinates_msg = Float64MultiArray()
        coordinates_data = []
        for pos in self.posiciones:
            coordinates_data.extend(pos)
        coordinates_msg.data = coordinates_data
        self.coordinates_publisher.publish(coordinates_msg)
        self.get_logger().info(f'\nCOORDENADAS DEL EFECTOR FINAL PUBLICADAS en {self.posiciones}')
    
    # VERIFICACIÓN DE LÍMITES
    def verificar_limites(self, x, y):
        error = False
        if x >= (self.largo_plano - (self.largo_efector / 2)):
            self.get_logger().error(f"FUERA DEL LÍMITE en x = {x}")
            error = True
        elif x <= (self.largo_efector / 2):
            self.get_logger().error(f"FUERA DEL LÍMITE en x = {x}")
            error = True
        if y >= (self.alto_plano - (self.alto_efector / 2)):
            self.get_logger().error(f"FUERA DEL LÍMITE en y = {y}")
            error = True
        elif y <= (self.alto_efector / 2):
            self.get_logger().error(f"FUERA DEL LÍMITE en y = {y}")
            error = True
        return error
    
    # VERIFICACIÓN DE COORDENADAS
    def verificar_todas_posiciones(self):
        errores = False
        for i, (x, y) in enumerate(self.posiciones):
            if self.verificar_limites(x, y):
                self.get_logger().error(f"Error en la posición {i+1}: ({x}, {y})")
                errores = True
        return errores
    
    # EFECTOR FINAL
    def calcular_esquinas(self, x, y):

        # Esquina superior izquierda (x1, y1)
        x1 = x - (self.largo_efector / 2)
        y1 = y + (self.alto_efector / 2)

        # Esquina superior derecha (x2, y2)
        x2 = x + (self.largo_efector / 2)
        y2 = y + (self.alto_efector / 2)

        # Esquina inferior izquierda (x3, y3)
        x3 = x - (self.largo_efector / 2)
        y3 = y - (self.alto_efector / 2)

        # Esquina inferior derecha (x4, y4)
        x4 = x + (self.largo_efector / 2)
        y4 = y - (self.alto_efector / 2)
        return x1, y1, x2, y2, x3, y3, x4, y4
    
    # CABLES
    def calcular_cables(self, x, y):

        x1, y1, x2, y2, _, _, _, _ = self.calcular_esquinas(x, y)

        # Cable esquina superior izquierda M1 = (M1x, M1y)
        M1x = 0
        M1y = self.alto_plano

        # Cable esquina superior derecha M2 = (M2x, M2y)
        M2x = self.largo_plano
        M2y = self.alto_plano

        # LONGITUDES DE LOS CABLES
        L1 = np.sqrt((x1 - M1x) ** 2 + (y1 - M1y) ** 2)
        L2 = np.sqrt((x2 - M2x) ** 2 + (y2 - M2y) ** 2)

        # ÁNGULOS
        q1 = -np.degrees(np.arctan((x1 - M1x) / (y1 - M1y)))
        q2 = np.degrees(np.arctan((x2 - M2x) / (y2 - M2y)))

        return L1, L2, q1, q2
    
    def dibujar_estructura(self):

        # PLANO
        fig, ax = plt.subplots(figsize=(20, 16))
        ax.set_xlim([-self.largo_plano * 0.25, self.largo_plano * 1.25])
        ax.set_ylim([-self.alto_plano * 0.5, self.alto_plano * 1.25])
        ax.set_xlabel('Eje X (centímetros)')
        ax.set_ylabel('Eje Y (centímetros)')
        ax.set_title('Robot por cables para el control de un efector final')

        # ESTRUCTURA
        ax.plot([0, 0], [self.alto_plano, -(self.alto_plano / 2)], 'k', linewidth=5)
        ax.plot([self.largo_plano, self.largo_plano], [self.alto_plano, -(self.alto_plano / 2)], 'k', linewidth=5)
        ax.plot([0, self.largo_plano], [self.alto_plano, self.alto_plano], 'k', linewidth=5)
        ax.plot([0, self.largo_plano], [0, 0], 'k', linewidth=5)
        ax.plot([-5, 5], [-(self.alto_plano / 2), -(self.alto_plano / 2)], 'k', linewidth=5)
        ax.plot([self.largo_plano - 5, self.largo_plano + 5], [-(self.alto_plano / 2), -(self.alto_plano / 2)], 'k', linewidth=5)

        # REPRESENTACIÓN RUEDAS
        ax.plot(0, self.alto_plano, 'ko', markersize=self.radio_rueda, markerfacecolor='black')
        ax.plot(0, self.alto_plano, 'wo', markersize=self.radio_rueda / 2, markerfacecolor='black')
        ax.plot(self.largo_plano, self.alto_plano, 'ko', markersize=self.radio_rueda, markerfacecolor='black')
        ax.plot(self.largo_plano, self.alto_plano, 'wo', markersize=self.radio_rueda / 2, markerfacecolor='black')

        # ELEMENTOS ANIMADOS
        efector, = ax.plot([], [], 'black', linewidth=2)
        centro_efector, = ax.plot([], [], 'ko', markersize=2, markerfacecolor='black')
        cable1, = ax.plot([], [], 'r', linewidth=2)
        cable2, = ax.plot([], [], 'r', linewidth=2)
        trayectoria, = ax.plot([], [], 'b--', linewidth=1, alpha=0.5)
        trayectoria_x = []
        trayectoria_y = []

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
            segmentos = self.num_posiciones - 1
            frames_por_segmento = 100 // segmentos
            segmento_actual = min(i // frames_por_segmento, segmentos - 1)
            progreso = (i % frames_por_segmento) / frames_por_segmento

            # POSICIÓN INICIAL Y FINAL DEL SEGMENTO ACTUAL
            x_inicio, y_inicio = self.posiciones[segmento_actual]
            x_fin, y_fin = self.posiciones[segmento_actual + 1]

            # CÁLCULO DE LA POSICIÓN ACTUAL
            x = x_inicio + (x_fin - x_inicio) * progreso
            y = y_inicio + (y_fin - y_inicio) * progreso

            # ESQUINAS EFECTOR FINAL
            x1, y1, x2, y2, x3, y3, x4, y4 = self.calcular_esquinas(x, y)

            # REPRESENTACIÓN EFECTOR FINAL
            xe = [x3, x4, x2, x1, x3]
            ye = [y3, y4, y2, y1, y3]
            efector.set_data(xe, ye)
            centro_efector.set_data(x, y)

            # CABLES

            # Cable esquina superior izquierda M1 = (M1x, M1y)
            M1x = 0
            M1y = self.alto_plano

            # Cable esquina superior derecha M2 = (M2x, M2y)
            M2x = self.largo_plano
            M2y = self.alto_plano
            
            # ACTUALIZACIÓN DE LA POSICIÓN DE LOS CABLES
            cable1.set_data([M1x, x1], [M1y, y1])
            cable2.set_data([M2x, x2], [M2y, y2])

            # ACTUALIZACIÓN DE LA TRAYECTORIA
            trayectoria_x.append(x)
            trayectoria_y.append(y)
            trayectoria.set_data(trayectoria_x, trayectoria_y)

            return efector, centro_efector, cable1, cable2, trayectoria

        # CREACIÓN DE LA ANIMACIÓN
        ani = FuncAnimation(fig, 
                            animate, 
                            frames=100, 
                            init_func=init,
                            blit=True, 
                            interval=50, 
                            repeat=False)

        # MOSTRAR DATOS DE CADA POSICIÓN
        cable_data = []
        for i, (x, y) in enumerate(self.posiciones):
            L1, L2, q1, q2 = self.calcular_cables(x, y)
            cable_data.extend([L1, L2, q1, q2])
            self.get_logger().info(f"DATOS POSICIÓN NÚMERO {i+1}")
            self.get_logger().info(f"Longitud del cable L1 = {L1} cm")
            self.get_logger().info(f"Longitud del cable L2 = {L2} cm")
            self.get_logger().info(f"Ángulo del cable L1 (q1) = {q1} °")
            self.get_logger().info(f"Ángulo del cable L2 (q2) = {q2} °")
        
        # PUBLICACIÓN DE LAS LONGITUDES DE LOS CABLES Y ÁNGULOS
        cable_msg = Float64MultiArray()
        cable_msg.data = cable_data
        self.cable_publisher.publish(cable_msg)

        # LONGITUD DE CABLE ELONGADA / RECOGIDA Y ÁNGULO DE GIRO DE CADA POLEA
        pulley_data = []
        for i in range(self.num_posiciones - 1):
            self.get_logger().info(f"\nLONGITUD DE CABLE ELONGADA / RECOGIDA Y ÁNGULO DE GIRO DE CADA POLEA ENTRE LAS POSICIONES {i+1} Y {i+2}")
            L1_inicial, L2_inicial, q1_inicial, q2_inicial = self.calcular_cables(self.posiciones[i][0], self.posiciones[i][1])
            L1_final, L2_final, q1_final, q2_final = self.calcular_cables(self.posiciones[i+1][0], self.posiciones[i+1][1])
            L1_movido = L1_final - L1_inicial
            L2_movido = L2_final - L2_inicial
            P1_movido_radianes = L1_movido / self.radio_rueda
            P2_movido_radianes = L2_movido / self.radio_rueda
            P1_movido_grados = np.degrees(P1_movido_radianes)
            P2_movido_grados = np.degrees(P2_movido_radianes)
            pulley_data.extend([L1_movido, L2_movido, P1_movido_radianes, P1_movido_grados, P2_movido_radianes, P2_movido_grados])
            self.get_logger().info(f"Longitud de cable elongada / recogida por el cable L1 = {L1_movido} cm")
            self.get_logger().info(f"Longitud de cable elongada / recogida por el cable L2 = {L2_movido} cm")
            self.get_logger().info(f"Ángulo girado por la polea P1 = {P1_movido_radianes} radianes")
            self.get_logger().info(f"Ángulo girado por la polea P1 = {P1_movido_grados} °")
            self.get_logger().info(f"Ángulo girado por la polea P2 = {P2_movido_radianes} radianes")
            self.get_logger().info(f"Ángulo girado por la polea P2 = {P2_movido_grados} °")
        
        # PUBLICACIÓN DE LOS PARÁMETROS DE LAS POLEAS
        pulley_msg = Float64MultiArray()
        pulley_msg.data = pulley_data
        self.pulley_publisher.publish(pulley_msg)
        self.get_logger().info("PARÁMETROS DE LAS POLEAS PUBLICADOS")
        
        plt.show()

def main(args=None):
    try:
        rclpy.init(args=args)
        version3_node = Version3Node()
        rclpy.spin(version3_node)
    except KeyboardInterrupt:
        print('... exiting version3_node')
    except Exception as e:
        print(e)
    finally:
        version3_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()