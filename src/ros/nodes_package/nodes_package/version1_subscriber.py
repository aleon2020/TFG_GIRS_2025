# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# colcon build --symlink-install
# ros2 run nodes_package version1_subscriber

class Version1Subscriber(Node):

    def __init__(self):
        super().__init__('version1_subscriber')
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

    def cable_callback(self, msg):
        if len(msg.data) == 4:
            L1, L2, q1, q2 = msg.data
            self.get_logger().info(
                f'\nLONGITUDES DE LOS CABLES RECIBIDAS\n'
                f'L1 = {L1} cm\n'
                f'L2 = {L2} cm\n'
                f'ÁNGULOS RECIBIDOS\n'
                f'q1 = {q1} °\n'
                f'q2 = {q2} °'
            )
        else:
            self.get_logger().error(f'Longitud / Ángulos de los cables incorrectos / fuera de rango: {msg.data}')

    def coordinates_callback(self, msg):
        if len(msg.data) == 2:
            x, y = msg.data
            self.get_logger().info(f'COORDENADAS DEL EFECTOR FINAL RECIBIDAS en x = {x}, y = {y}')
        else:
            self.get_logger().error(f'Coordenadas incorrectas / fuera de rango: {msg.data}')

def main(args=None):
    try:
        rclpy.init(args=args)
        version1_subscriber = Version1Subscriber()
        rclpy.spin(version1_subscriber)
    except KeyboardInterrupt:
        print('... exiting version1_subscriber')
    except Exception as e:
        print(e)
    finally:
        version1_subscriber.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()