import rclpy
from math import sin, cos, pi
from rclpy.node import Node
from rclpy.qos import QoSProfile
from geometry_msgs.msg import Quaternion, Twist
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster, TransformStamped

class RobotController(Node):

    def __init__(self):
        super().__init__('robot_controller')
        qos_profile = QoSProfile(depth=10)
        self.time_last = self.get_clock().now()
        self.odom = {'x':0.0, 'y':0.0, 'th':0.0}
        self.left_wheel_joint_pos = 0
        self.right_wheel_joint_pos = 0
        self.cmd_vel = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, qos_profile)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', qos_profile)
        self.broadcaster = TransformBroadcaster(self, qos=qos_profile)
        self.get_logger().info(f"{self.get_name()} started")
        
    def cmd_vel_callback(self, msg):
        vx = msg.linear.x
        vy = 0.0
        vr = msg.angular.z
        time_now = self.get_clock().now()
        vx_real = vx
        vy_real = vy
        vr_real = vr
        self.update_joint_positions(vx_real, vy_real, vr_real, time_now)
        self.update_odom(vx_real, vy_real, vr_real, time_now)
        x = self.odom['x']
        y = self.odom['y']
        th = self.odom['th']
        odom_trans = TransformStamped()
        odom_trans.header.frame_id = 'odom'
        odom_trans.child_frame_id = 'base_link'
        odom_trans.header.stamp = time_now.to_msg()
        odom_trans.transform.translation.x = x
        odom_trans.transform.translation.y = y
        odom_trans.transform.translation.z = 0.0
        odom_trans.transform.rotation = euler_to_quaternion(0, 0, th)
        self.get_logger().info(f"x: {x}")
        self.get_logger().info(f"y: {y}")
        self.get_logger().info(f"th: {th}")
        joint_state = JointState()
        joint_state.header.stamp = time_now.to_msg()
        joint_state.name = ['left_wheel_joint', 'right_wheel_joint']
        joint_state.position = [self.left_wheel_joint_pos, self.right_wheel_joint_pos]
        self.joint_pub.publish(joint_state)
        self.broadcaster.sendTransform(odom_trans)

    def update_odom(self, vx, vy, vr, time_now):
        dt = (time_now.nanoseconds - self.time_last.nanoseconds) * 10**-9
        if dt > 0.1: dt = 0
        self.time_last = time_now
        delta_th = vr*dt
        delta_x = (vx * cos(delta_th) - vy * sin(delta_th)) * dt
        delta_y = (vx * sin(delta_th) + vy * cos(delta_th)) * dt
        self.odom['x'] += cos(self.odom['th']) * delta_x - sin(self.odom['th']) * delta_y
        self.odom['y'] += sin(self.odom['th']) * delta_x + cos(self.odom['th']) * delta_y
        self.odom['th'] += delta_th

    def update_joint_positions(self, vx, vy, vr, time_now):
        L = 10
        r = 0.5
        l_omega = (vx - (L/2)*vr)/r
        r_omega = (vx + (L/2)*vr)/r
        dt = (time_now.nanoseconds - self.time_last.nanoseconds) * 10**-9
        self.left_wheel_joint_pos += l_omega * dt
        self.right_wheel_joint_pos += r_omega * dt

def euler_to_quaternion(roll, pitch, yaw):
    qx = sin(roll/2) * cos(pitch/2) * cos(yaw/2) - cos(roll/2) * sin(pitch/2) * sin(yaw/2)
    qy = cos(roll/2) * sin(pitch/2) * cos(yaw/2) + sin(roll/2) * cos(pitch/2) * sin(yaw/2)
    qz = cos(roll/2) * cos(pitch/2) * sin(yaw/2) - sin(roll/2) * sin(pitch/2) * cos(yaw/2)
    qw = cos(roll/2) * cos(pitch/2) * cos(yaw/2) + sin(roll/2) * sin(pitch/2) * sin(yaw/2)
    return Quaternion(x=qx, y=qy, z=qz, w=qw)

def main(args=None):
    try:
        rclpy.init(args=args)
        robot_controller = RobotController()
        rclpy.spin(robot_controller)
    except KeyboardInterrupt: 
        print(' ... exit node')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()