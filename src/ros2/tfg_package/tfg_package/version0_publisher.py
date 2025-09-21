import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Version0Publisher(Node):

    def __init__(self):
        super().__init__('version0_publisher')
        self.publisher = self.create_publisher(String, 'version0_topic', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = "message # %d" %self.i
        self.publisher.publish(msg)
        self.get_logger().info("Publishing: %s" % msg.data)
        self.i += 1

def main(args=None):
    try:
        rclpy.init(args=args)
        version0_publisher = Version0Publisher()
        rclpy.spin(version0_publisher)
    except KeyboardInterrupt:
        print('... exiting version0_publisher')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()