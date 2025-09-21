import rclpy
from rclpy.node import Node

class Version0Node(Node):

    def __init__(self):
        super().__init__('version0_node')
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        print('MENSAJE DE PRUEBA')

def main(args=None):
    try:
        rclpy.init(args=args)
        version0_node = Version0Node()
        rclpy.spin(version0_node)
    except KeyboardInterrupt:
        print('... exiting version0_node')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()