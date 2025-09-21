# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# colcon build --symlink-install
# ros2 run tfg_package version3_subscriber

class Version3Subscriber(Node):

    def __init__(self):
        super().__init__('version3_subscriber')
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
        num_posiciones = len(msg.data) // 4
        if len(msg.data) % 4 == 0 and num_posiciones >= 1:
            log_msg = ''
            for i in range(num_posiciones):
                idx = i * 4
                L1, L2, q1, q2 = msg.data[idx:idx+4]
                log_msg += (
                    f'\nDATOS RECIBIDOS DE LA POSICIÓN NÚMERO {i+1}\n'
                    f'L1 = {L1} cm\n'
                    f'L2 = {L2} cm\n'
                    f'q1 = {q1} °\n'
                    f'q2 = {q2} °\n'
                )
            self.get_logger().info(log_msg)
        else:
            self.get_logger().error(f'Longitud / Ángulos de los cables incorrectos / fuera de rango: {msg.data}')

    def coordinates_callback(self, msg):
        num_posiciones = len(msg.data) // 2
        if len(msg.data) % 2 == 0 and num_posiciones >= 1:
            log_msg = '\nCOORDENADAS DEL EFECTOR FINAL RECIBIDAS\n'
            for i in range(num_posiciones):
                idx = i * 2
                x, y = msg.data[idx:idx+2]
                log_msg += f'POSICIÓN {i+1}: x = {x}, y = {y}\n'
            self.get_logger().info(log_msg)
        else:
            self.get_logger().error(f'Coordenadas incorrectas / fuera de rango: {msg.data}')

def main(args=None):
    try:
        rclpy.init(args=args)
        version3_subscriber = Version3Subscriber()
        rclpy.spin(version3_subscriber)
    except KeyboardInterrupt:
        print('... exiting version3_subscriber')
    except Exception as e:
        print(e)
    finally:
        version3_subscriber.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()