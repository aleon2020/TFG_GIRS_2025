# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# colcon build --symlink-install
# ros2 run nodes_package version0_subscriber

class Version0Subscriber(Node):

    def __init__(self):
        super().__init__('version0_subscriber')
        self.subscription = self.create_subscription(
            String,
            'version0_topic',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        self.get_logger().info('received : "%s"' % msg.data)

def main(args=None):
    try:
        rclpy.init(args=args)
        version0_subscriber = Version0Subscriber()
        rclpy.spin(version0_subscriber)
    except KeyboardInterrupt:
        print('... exiting version0_subscriber')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()