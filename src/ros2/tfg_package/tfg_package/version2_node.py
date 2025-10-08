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
# ros2 run tfg_package version2_node

class Version2Node(Node):

    # PARÁMETROS
    def __init__(self):
        super().__init__('version2_node')
        self.declare_parameters(
            namespace='',
            parameters=[
                ('largo_plano', 100),
                ('alto_plano', 100),
                ('largo_efector', 10),
                ('alto_efector', 10),
                ('radio_rueda', 5)
            ]
        )
        self.largo_plano = self.get_parameter('largo_plano').value
        self.alto_plano = self.get_parameter('alto_plano').value
        self.largo_efector = self.get_parameter('largo_efector').value
        self.alto_efector = self.get_parameter('alto_efector').value
        self.radio_rueda = self.get_parameter('radio_rueda').value
        self.cable_publisher = self.create_publisher(Float64MultiArray, 'cable_parameters', 10)
        self.coordinates_publisher = self.create_publisher(Float64MultiArray, 'effector_coordinates', 10)
        self.pulley_publisher = self.create_publisher(Float64MultiArray, 'pulley_parameters', 10)
        self.solicitar_coordenadas()
        self.publicar_coordenadas()
        if not self.verificar_limites(self.x_inicial, self.y_inicial) and not self.verificar_limites(self.x_final, self.y_final):
            self.dibujar_estructura()
    
    # SOLICITUD DE LAS COORDENADAS DEL EFECTOR FINAL
    def solicitar_coordenadas(self):
        try:
            print("\nCOORDENADAS INICIALES DEL EFECTOR FINAL")
            self.x_inicial = float(input('Coordenada x inicial del efector final: '))
            self.y_inicial = float(input('Coordenada y inicial del efector final: '))
            print("\nCOORDENADAS FINALES DEL EFECTOR FINAL")
            self.x_final = float(input('Coordenada x final del efector final: '))
            self.y_final = float(input('Coordenada y final del efector final: '))
            print()
        except ValueError:
            self.get_logger().error("Coordenadas incorrectas / fuera de rango")
            sys.exit(1)
    
    # PUBLICACIÓN DE LAS COORDENADAS DEL EFECTOR FINAL
    def publicar_coordenadas(self):
        coordinates_msg = Float64MultiArray()
        coordinates_msg.data = [self.x_inicial, self.y_inicial, self.x_final, self.y_final]
        self.coordinates_publisher.publish(coordinates_msg)
        self.get_logger().info(f'COORDENADAS DEL EFECTOR FINAL en inicio = ({self.x_inicial}, {self.y_inicial}), final = ({self.x_final}, {self.y_final})')
    
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

        # REPRESENTACIÓN RUEDAS (fijas)
        ax.plot(0, self.alto_plano, 'ko', markersize=self.radio_rueda, markerfacecolor='black')
        ax.plot(0, self.alto_plano, 'wo', markersize=self.radio_rueda / 2, markerfacecolor='black')
        ax.plot(self.largo_plano, self.alto_plano, 'ko', markersize=self.radio_rueda, markerfacecolor='black')
        ax.plot(self.largo_plano, self.alto_plano, 'wo', markersize=self.radio_rueda / 2, markerfacecolor='black')

        # ACTUALIZACIÓN DE LA POSICIÓN DE LOS ELEMENTOS DESPLAZADOS
        efector, = ax.plot([], [], 'black', linewidth=2)
        centro_efector, = ax.plot([], [], 'ko', markersize=2, markerfacecolor='black')
        cable1, = ax.plot([], [], 'r', linewidth=2)
        cable2, = ax.plot([], [], 'r', linewidth=2)
        trayectoria, = ax.plot([], [], 'b--', linewidth=1, alpha=0.5)

        # ALMACENAMIENTO DE LOS PUNTOS DE LA TRAYECTORIA REALIZADA
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
            t = i / 100
            x = self.x_inicial + (self.x_final - self.x_inicial) * t
            y = self.y_inicial + (self.y_final - self.y_inicial) * t

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

        # CALCULAR Y PUBLICAR PARÁMETROS DE CABLES
        L1_inicial, L2_inicial, q1_inicial, q2_inicial = self.calcular_cables(self.x_inicial, self.y_inicial)
        L1_final, L2_final, q1_final, q2_final = self.calcular_cables(self.x_final, self.y_final)
        
        # LONGITUD Y ÁNGULO DE CADA CABLE EN LA POSICIÓN INICIAL
        self.get_logger().info("\nDATOS POSICIÓN INICIAL")
        self.get_logger().info(f"Longitud del cable L1 = {L1_inicial} cm")
        self.get_logger().info(f"Longitud del cable L2 = {L2_inicial} cm")
        self.get_logger().info(f"Ángulo del cable L1 (q1) = {q1_inicial} °")
        self.get_logger().info(f"Ángulo del cable L2 (q2) = {q2_inicial} °")

        # LONGITUD Y ÁNGULO DE CADA CABLE EN LA POSICIÓN FINAL
        self.get_logger().info("\nDATOS POSICIÓN FINAL")
        self.get_logger().info(f"Longitud del cable L1 = {L1_final} cm")
        self.get_logger().info(f"Longitud del cable L2 = {L2_final} cm")
        self.get_logger().info(f"Ángulo del cable L1 (q1) = {q1_final} °")
        self.get_logger().info(f"Ángulo del cable L2 (q2) = {q2_final} °")
        
        # PUBLICACIÓN DE LAS LONGITUDES DE LOS CABLES Y ÁNGULOS
        cable_msg = Float64MultiArray()
        cable_msg.data = [L1_inicial, L2_inicial, q1_inicial, q2_inicial, 
                         L1_final, L2_final, q1_final, q2_final]
        self.cable_publisher.publish(cable_msg)

        # LONGITUD DE CABLE ELONGADA / RECOGIDA Y ÁNGULO DE GIRO DE CADA POLEA
        self.get_logger().info("\nLONGITUD DE CABLE ELONGADA / RECOGIDA Y ÁNGULO DE GIRO DE CADA POLEA")
        L1_movido = L1_final - L1_inicial
        L2_movido = L2_final - L2_inicial
        P1_movido_radianes = L1_movido / self.radio_rueda
        P2_movido_radianes = L2_movido / self.radio_rueda
        self.get_logger().info(f"Longitud de cable elongada / recogida por el cable L1 = {L1_movido} cm")
        self.get_logger().info(f"Longitud de cable elongada / recogida por el cable L2 = {L2_movido} cm")
        self.get_logger().info(f"Ángulo girado por la polea P1 = {P1_movido_radianes} radianes")
        self.get_logger().info(f"Ángulo girado por la polea P1 = {np.degrees(P1_movido_radianes)} °")
        self.get_logger().info(f"Ángulo girado por la polea P2 = {P2_movido_radianes} radianes")
        self.get_logger().info(f"Ángulo girado por la polea P2 = {np.degrees(P2_movido_radianes)} °")
        
        # PUBLICACIÓN DE LOS PARÁMETROS DE LAS POLEAS
        pulley_msg = Float64MultiArray()
        pulley_msg.data = [L1_movido, L2_movido, P1_movido_radianes, np.degrees(P1_movido_radianes), 
                          P2_movido_radianes, np.degrees(P2_movido_radianes)]
        self.pulley_publisher.publish(pulley_msg)

        plt.show()

def main(args=None):
    try:
        rclpy.init(args=args)
        version2_node = Version2Node()
        rclpy.spin(version2_node)
    except KeyboardInterrupt:
        print('... exiting version2_node')
    except Exception as e:
        print(e)
    finally:
        version2_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()