# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# colcon build --symlink-install
# ros2 run tfg_package version2_subscriber

class Version2Subscriber(Node):

    def __init__(self):
        super().__init__('version2_subscriber')
        self.cable_subscription = self.create_subscription(
            Float64MultiArray,
            'cable_parameters',
            self.cable_callback,
            10
        )
        self.coordinates_subscription = self.create_subscription(
            Float64MultiArray,
            'effector_coordinates',
            self.coordinates_callback,
            10
        )
        self.pulley_subscription = self.create_subscription(
            Float64MultiArray,
            'pulley_parameters',
            self.pulley_callback,
            10
        )

    def cable_callback(self, msg):
        if len(msg.data) == 8:
            L1_inicial, L2_inicial, q1_inicial, q2_inicial, L1_final, L2_final, q1_final, q2_final = msg.data
            self.get_logger().info(
                f'\nLONGITUDES DE LOS CABLES Y ÁNGULOS INICIALES RECIBIDOS\n'
                f'L1 = {L1_inicial} cm\n'
                f'L2 = {L2_inicial} cm\n'
                f'q1 = {q1_inicial} °\n'
                f'q2 = {q2_inicial} °\n'
                f'LONGITUDES DE LOS CABLES Y ÁNGULOS FINALES RECIBIDOS\n'
                f'L1 = {L1_final} cm\n'
                f'L2 = {L2_final} cm\n'
                f'q1 = {q1_final} °\n'
                f'q2 = {q2_final} °'
            )
        else:
            self.get_logger().error(f'Longitud / Ángulos de los cables incorrectos / fuera de rango: {msg.data}')

    def coordinates_callback(self, msg):
        if len(msg.data) == 4:
            x_inicial, y_inicial, x_final, y_final = msg.data
            self.get_logger().info(
                f'\nCOORDENADAS INICIALES DEL EFECTOR FINAL RECIBIDAS en x = {x_inicial}, y = {y_inicial}\n'
                f'COORDENADAS FINALES DEL EFECTOR FINAL RECIBIDAS en x = {x_final}, y = {y_final}'
            )
        else:
            self.get_logger().error(f'Coordenadas incorrectas / fuera de rango: {msg.data}')

    def pulley_callback(self, msg):
        if len(msg.data) == 6:
            L1_movido, L2_movido, P1_rad, P1_deg, P2_rad, P2_deg = msg.data
            self.get_logger().info(
                f'\nPARÁMETROS DE POLEAS RECIBIDOS\n'
                f'Longitud de cable elongada/recogida L1 = {L1_movido} cm\n'
                f'Longitud de cable elongada/recogida L2 = {L2_movido} cm\n'
                f'Ángulo girado por polea P1 = {P1_rad} radianes\n'
                f'Ángulo girado por polea P1 = {P1_deg} °\n'
                f'Ángulo girado por polea P2 = {P2_rad} radianes\n'
                f'Ángulo girado por polea P2 = {P2_deg} °'
            )
        else:
            self.get_logger().error(f'Parámetros de poleas incorrectos / fuera de rango: {msg.data}')

def main(args=None):
    try:
        rclpy.init(args=args)
        version2_subscriber = Version2Subscriber()
        rclpy.spin(version2_subscriber)
    except KeyboardInterrupt:
        print('... exiting version2_subscriber')
    except Exception as e:
        print(e)
    finally:
        version2_subscriber.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()