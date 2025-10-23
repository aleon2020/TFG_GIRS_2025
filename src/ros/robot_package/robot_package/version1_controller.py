# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
import math
from geometry_msgs.msg import Point
from sensor_msgs.msg import JointState
from interfaces_package.msg import EffectorPosition, CableParameters, PulleyParameters

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# TERMINAL 1: colcon build --symlink-install
# TERMINAL 2: ros2 run robot_package version1_controller
# TERMINAL 3: ros2 topic echo /effector_coordinates
# TERMINAL 4: ros2 topic echo /cable_parameters
# TERMINAL 5: ros2 topic echo /pulley_parameters
# TERMINAL 6: ros2 topic pub --once /version1 interfaces_package/msg/EffectorPosition "{position: {x: 0.30, y: 0.30}}"

class Version1Controller(Node):

    # Función __init__()
    # Inicializa el nodo, define parámetros del sistema y configura publicadores y subscriptores.
    def __init__(self):
        super().__init__('version1_controller')

        # PARÁMETROS FÍSICOS DEL SISTEMA
        self.plane_width = 1.0
        self.plane_height = 1.0
        self.effector_width = 0.1
        self.effector_height = 0.1
        self.pulley_radius = 0.05

        # POSICIONES INICIALES
        self.current_x = self.plane_width / 2.0
        self.current_y = self.plane_height / 2.0
        self.reference_x = self.plane_width / 2.0
        self.reference_y = self.plane_height / 2.0

        # CONFIGURACIÓN DE LA CALIDAD DE SERVICIO (QOS)
        qos_profile = QoSProfile(depth=10)

        # CREACIÓN DE PUBLICADORES
        self.effector_coordinates_publisher = self.create_publisher(EffectorPosition, '/effector_coordinates', qos_profile)
        self.cable_parameters_publisher = self.create_publisher(CableParameters, '/cable_parameters', qos_profile)
        self.pulley_parameters_publisher = self.create_publisher(PulleyParameters, '/pulley_parameters', qos_profile)
        self.joint_state_publisher = self.create_publisher(JointState, 'joint_states', qos_profile)

        # SUBSCRIPCIÓN AL TOPIC /VERSION1
        self.coordinates_subscriber = self.create_subscription(EffectorPosition, '/version1', self.position_callback, qos_profile)
        
        # CÁLCULO DE LOS PARÁMETROS INICIALES DE REFERENCIA
        (self.reference_left_cable_length, self.reference_right_cable_length, self.reference_left_cable_angle, self.reference_right_cable_angle) = self.calculate_cable_parameters(self.reference_x, self.reference_y)
        self.received = False
        self.get_logger().info("CONTROLADOR ACTIVADO. ESPERANDO COORDENADAS ...")

    # Función calculate_cable_parameters()
    # Calcula longitudes y ángulos de los cables en función de la posición del efector.
    def calculate_cable_parameters(self, x, y):

        # COORDENADAS DE LAS POLEAS
        left_pulley_x, left_pulley_y = 0.0, self.plane_height
        right_pulley_x, right_pulley_y = self.plane_width, self.plane_height

        # COORDENADAS DE LOS PUNTOS DE CONEXIÓN DEL EFECTOR CON LOS CABLES
        left_connection_x = x - self.effector_width / 2.0
        left_connection_y = y + self.effector_height / 2.0
        right_connection_x = x + self.effector_width / 2.0
        right_connection_y = y + self.effector_height / 2.0

        # CÁLCULO DE LAS LONGITUDES DE CADA CABLE
        left_cable_length = math.sqrt((left_connection_x - left_pulley_x)**2 + (left_connection_y - left_pulley_y)**2)
        right_cable_length = math.sqrt((right_connection_x - right_pulley_x)**2 + (right_connection_y - right_pulley_y)**2)
        
        # CÁLCULO DE LOS ÁNGULOS DE CADA CABLE
        left_cable_angle = math.degrees(math.atan2(left_connection_x - left_pulley_x, left_pulley_y - left_connection_y))
        right_cable_angle = math.degrees(math.atan2(right_pulley_x - right_connection_x, right_pulley_y - right_connection_y))
        
        return left_cable_length, right_cable_length, left_cable_angle, right_cable_angle

    # Función calculate_pulley_changes()
    # Calcula la longitud de cable recogida por las poleas en función de la posición del efector.
    def calculate_pulley_changes(self, x, y):
        l1, l2, _, _ = self.calculate_cable_parameters(x, y)

        # LONGITUD DE CABLE ELONGADO /RECOGIDO POR CADA POLEA
        delta_l1 = l1 - self.reference_left_cable_length
        delta_l2 = l2 - self.reference_right_cable_length

        # ÁNGULO GIRADO POR CADA POLEA
        pulley1_angle = delta_l1 / self.pulley_radius
        pulley2_angle = delta_l2 / self.pulley_radius

        return delta_l1, delta_l2, pulley1_angle, pulley2_angle

    # Función position_callback()
    # Procesa la posición recibida del efector y publica el resto de parámetros.
    def position_callback(self, msg):

        # IGNORACIÓN DEL PROCESAMIENTO DE MÚLTIPLES MENSAJES
        if self.received:
            return
        try:
            pos: Point = msg.position
        except AttributeError:
            self.get_logger().error("ERROR. FORMATO CORRECTO DEL MENSAJE: {position: {x:..., y:...}}")
            return
        
        self.received = True
        self.current_x, self.current_y = float(pos.x), float(pos.y)

        # CÁLCULO DE LA VARIACIÓN DE LA LONGITUD DE CABLE ELONGADA / RECOGIDA POR CADA POLEA
        delta_l1, delta_l2, pulley1_angle, pulley2_angle = self.calculate_pulley_changes(self.current_x, self.current_y)
        
        # CÁLCULO DE LA VARIACIÓN DEL ÁNGULO GIRADO POR CADA POLEA
        left_len, right_len, left_ang, right_ang = self.calculate_cable_parameters(self.current_x, self.current_y)
        
        # PUBLICACIÓN DE LA POSICIÓN ACTUAL DEL EFECTOR
        effector_message = EffectorPosition()
        effector_message.position.x = self.current_x
        effector_message.position.y = self.current_y
        self.effector_coordinates_publisher.publish(effector_message)

        # PUBLICACIÓN DE LOS PARÁMETROS DE CADA CABLE
        cable_message = CableParameters()
        cable_message.left_length = left_len
        cable_message.right_length = right_len
        cable_message.left_angle = left_ang
        cable_message.right_angle = right_ang
        self.cable_parameters_publisher.publish(cable_message)

        # PUBLICACIÓN DE LOS PARÁMETROS DE CADA POLEA
        pulley_message = PulleyParameters()
        pulley_message.left_cable_change = delta_l1
        pulley_message.right_cable_change = delta_l2
        pulley_message.left_pulley_angle = pulley1_angle
        pulley_message.right_pulley_angle = pulley2_angle
        self.pulley_parameters_publisher.publish(pulley_message)

        # PUBLICACIÓN DEL JOINT STATE DE CADA POLEA (RVIZ)
        joint_state_message = JointState()
        joint_state_message.header.stamp = self.get_clock().now().to_msg()
        joint_state_message.name = ['left_wheel_joint', 'right_wheel_joint']
        joint_state_message.position = [pulley1_angle, pulley2_angle]
        self.joint_state_publisher.publish(joint_state_message)

        # VISUALIZACIÓN DE LOS RESULTADOS
        print("=" * 100)
        print("POSICIÓN DEL EFECTOR FINAL (X, Y)")
        print(f"• POSICIÓN OBJETIVO: ({self.current_x:.3f}, {self.current_y:.3f}) m")
        print(f"LONGITUDES DE CADA CABLE (L1, L2)")
        print(f"• L1: {left_len:.3f} m, L2: {right_len:.3f} m")
        print("ÁNGULOS DE CADA CABLE (Q1, Q2)")
        print(f"• Q1: {left_ang:.2f} °, Q2: {right_ang:.2f} °")
        print("MOVIMIENTO DE CADA POLEA (P1, P2)")
        print(f"• CABLE ELONGADO / RECOGIDO:  P1: {delta_l1:+.3f} m,   P2: {delta_l2:+.3f} m")
        print(f"• ÁNGULOS DE GIRO (RADIANES): P1: {pulley1_angle:+.3f} rad, P2: {pulley2_angle:+.3f} rad")
        print("=" * 100)
        self.get_logger().info("CERRANDO CONTROLADOR ...")
        self.create_timer(3.0, self.shutdown_node)

    # Función shutdown_node()
    # Cierra el nodo y detiene su ejecución.
    def shutdown_node(self):
        self.destroy_node()
        rclpy.shutdown()

# Función principal main()
# Punto de entrada del programa.
def main(args=None):
    rclpy.init(args=args)
    controller = Version1Controller()
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        print("\nCERRANDO CONTROLADOR ...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            if rclpy.ok():
                controller.destroy_node()
                rclpy.shutdown()
        except:
            pass

if __name__ == '__main__':
    main()