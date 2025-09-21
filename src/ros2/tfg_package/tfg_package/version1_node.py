# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.
import rclpy
from rclpy.node import Node
import numpy as np
import matplotlib.pyplot as plt
from std_msgs.msg import Float64MultiArray
import sys

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# colcon build --symlink-install
# ros2 run tfg_package version1_node

class Version1Node(Node):

    # PARÁMETROS
    def __init__(self):
        super().__init__('version1_node')
        self.declare_parameters(
            namespace='',
            parameters=[
                ('largo_plano', 100),
                ('alto_plano', 100),
                ('largo_efector', 10),
                ('alto_efector', 10),
                ('radio_rueda', 25)
            ]
        )
        self.largo_plano = self.get_parameter('largo_plano').value
        self.alto_plano = self.get_parameter('alto_plano').value
        self.largo_efector = self.get_parameter('largo_efector').value
        self.alto_efector = self.get_parameter('alto_efector').value
        self.radio_rueda = self.get_parameter('radio_rueda').value
        self.cable_publisher = self.create_publisher(Float64MultiArray, 'cable_parameters', 10)
        self.coordinates_publisher = self.create_publisher(Float64MultiArray, 'effector_coordinates', 10)
        self.solicitar_coordenadas()
        self.publicar_coordenadas()
        if not self.verificar_limites():
            self.dibujar_estructura()
    
    # SOLICITUD DE LAS COORDENADAS DEL EFECTOR FINAL
    def solicitar_coordenadas(self):
        try:
            print("\nCOORDENADAS DEL EFECTOR FINAL")
            self.x_efector = float(input('Coordenada x del efector final: '))
            self.y_efector = float(input('Coordenada y del efector final: '))
            print()
        except ValueError:
            self.get_logger().error("Coordenadas incorrectas / fuera de rango")
            sys.exit(1)
    
    # PUBLICACIÓN DE LAS COORDENADAS DEL EFECTOR FINAL
    def publicar_coordenadas(self):
        coordinates_msg = Float64MultiArray()
        coordinates_msg.data = [self.x_efector, self.y_efector]
        self.coordinates_publisher.publish(coordinates_msg)
        self.get_logger().info(f'COORDENADAS DEL EFECTOR FINAL en x = {self.x_efector}, y = {self.y_efector}')
    
    # VERIFICACIÓN DE LÍMITES
    def verificar_limites(self):
        error = False
        if self.x_efector >= (self.largo_plano - (self.largo_efector / 2)):
            self.get_logger().error(f"FUERA DEL LÍMITE en x = {self.x_efector}")
            error = True
        elif self.x_efector <= (self.largo_efector / 2):
            self.get_logger().error(f"FUERA DEL LÍMITE en x = {self.x_efector}")
            error = True
        if self.y_efector >= (self.alto_plano - (self.alto_efector / 2)):
            self.get_logger().error(f"FUERA DEL LÍMITE en y = {self.y_efector}")
            error = True
        elif self.y_efector <= (self.alto_efector / 2):
            self.get_logger().error(f"FUERA DEL LÍMITE en y = {self.y_efector}")
            error = True
        return error
    
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

        # EFECTOR FINAL

        # Esquina superior izquierda (x1, y1)
        x1 = self.x_efector - (self.largo_efector / 2)
        y1 = self.y_efector + (self.alto_efector / 2)

        # Esquina superior derecha (x2, y2)
        x2 = self.x_efector + (self.largo_efector / 2)
        y2 = self.y_efector + (self.alto_efector / 2)

        # Esquina inferior izquierda (x3, y3)
        x3 = self.x_efector - (self.largo_efector / 2)
        y3 = self.y_efector - (self.alto_efector / 2)

        # Esquina inferior derecha (x4, y4)
        x4 = self.x_efector + (self.largo_efector / 2)
        y4 = self.y_efector - (self.alto_efector / 2)

        # CABLES

        # Cable esquina superior izquierda M1 = (M1x, M1y)
        M1x = 0
        M1y = self.alto_plano
        ax.plot([M1x, x1], [M1y, y1], 'r', linewidth=2)

        # Cable esquina superior derecha M2 = (M2x, M2y)
        M2x = self.largo_plano
        M2y = self.alto_plano
        ax.plot([M2x, x2], [M2y, y2], 'r', linewidth=2)

        # REPRESENTACIÓN EFECTOR FINAL
        xe = [x3, x4, x2, x1, x3]
        ye = [y3, y4, y2, y1, y3]
        ax.plot(xe, ye, 'black', linewidth=2)
        ax.plot(self.x_efector, self.y_efector, 'ko', markersize=2, markerfacecolor='black')

        # REPRESENTACIÓN RUEDAS
        ax.plot(0, self.alto_plano, 'ko', markersize=self.radio_rueda, markerfacecolor='black')
        ax.plot(0, self.alto_plano, 'wo', markersize=self.radio_rueda / 2, markerfacecolor='black')
        ax.plot(self.largo_plano, self.alto_plano, 'ko', markersize=self.radio_rueda, markerfacecolor='black')
        ax.plot(self.largo_plano, self.alto_plano, 'wo', markersize=self.radio_rueda / 2, markerfacecolor='black')

        # LONGITUDES DE LOS CABLES Y ÁNGULOS
        L1 = np.sqrt((x1 - M1x) ** 2 + (y1 - M1y) ** 2)
        L2 = np.sqrt((x2 - M2x) ** 2 + (y2 - M2y) ** 2)
        q1 = -np.degrees(np.arctan((x1 - M1x) / (y1 - M1y)))
        q2 = np.degrees(np.arctan((x2 - M2x) / (y2 - M2y)))
        self.get_logger().info(f"Longitud del cable L1 = {L1} cm")
        self.get_logger().info(f"Longitud del cable L2 = {L2} cm")
        self.get_logger().info(f"Ángulo del cable L1 (q1) = {q1} °")
        self.get_logger().info(f"Ángulo del cable L2 (q2) = {q2} °")
        
        # PUBLICACIÓN DE LAS LONGITUDES DE LOS CABLES Y ÁNGULOS
        cable_msg = Float64MultiArray()
        cable_msg.data = [L1, L2, q1, q2]
        self.cable_publisher.publish(cable_msg)
        
        plt.show()

def main(args=None):
    try:
        rclpy.init(args=args)
        version1_node = Version1Node()
        rclpy.spin(version1_node)
    except KeyboardInterrupt:
        print('... exiting version1_node')
    except Exception as e:
        print(e)
    finally:
        version1_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()