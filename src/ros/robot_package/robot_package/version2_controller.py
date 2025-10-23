# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
import math
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from tf2_ros import TransformBroadcaster
from interfaces_package.msg import EffectorCoordinates, CableParameters, PulleyParameters

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# TERMINAL 1: colcon build --symlink-install
# TERMINAL 2: ros2 run robot_package version2_controller
# TERMINAL 3: ros2 topic echo /effector_coordinates
# TERMINAL 4: ros2 topic echo /cable_parameters
# TERMINAL 5: ros2 topic echo /pulley_parameters
# TERMINAL 6: ros2 topic echo /effector_log
# TERMINAL 7: ros2 topic echo /cable_log
# TERMINAL 8: ros2 topic echo /pulley_log
# TERMINAL 9: ros2 topic pub --once /version2 interfaces_package/msg/EffectorCoordinates "{current: {x: 0.30, y: 0.30}, target: {x: 0.70, y: 0.70}}"

class Version2Controller(Node):

    # Función __init__()
    # Inicializa el nodo, define parámetros del sistema y configura publicadores y subscriptores.
    def __init__(self):
        super().__init__('version2_controller')

        # PARÁMETROS GEOMÉTRICOS DEL SISTEMA
        self.plane_width = 1.0
        self.plane_height = 1.0  
        self.effector_width = 0.1
        self.effector_height = 0.1
        self.pulley_radius = 0.05

        # VARIABLES DE ESTADO
        self.current_x = 0.5
        self.current_y = 0.5
        self.target_x = 0.5
        self.target_y = 0.5
        self.moving = False
        self.animation_progress = 0.0
        self.objective_achieved = False
        self.shutdown_scheduled = False

        # VARIABLES AUXILIARES
        self.initial_x = self.current_x
        self.initial_y = self.current_y
        self.target_left_cable_length = 0.0
        self.target_right_cable_length = 0.0
        self.target_left_cable_angle = 0.0
        self.target_right_cable_angle = 0.0
        self.target_left_cable_change = 0.0
        self.target_right_cable_change = 0.0
        self.target_left_pulley_angle = 0.0
        self.target_right_pulley_angle = 0.0
        self.left_pulley_positioition = 0.0
        self.right_pulley_position = 0.0

        # TIMERS DE CONTROL PARA PUBLICACIONES PERIÓDICAS
        self.control_timer = self.create_timer(0.1, self.control_loop)
        self.effector_timer = self.create_timer(0.25, self.publish_effector_parameters)
        self.cable_timer = self.create_timer(0.25, self.publish_cable_parameters)
        self.pulley_timer = self.create_timer(0.25, self.publish_pulley_parameters)

        # CONFIGURACIÓN DE LA COMUNICACIÓN QOS
        qos_profile = QoSProfile(depth=10)
        self.effector_coordinates_publisher = self.create_publisher(EffectorCoordinates, '/effector_coordinates', qos_profile)
        self.cable_parameters_publisher = self.create_publisher(CableParameters, '/cable_parameters', qos_profile)
        self.pulley_parameters_publisher = self.create_publisher(PulleyParameters, '/pulley_parameters', qos_profile)
        self.joint_state_publisher = self.create_publisher(JointState, 'joint_states', qos_profile)
        self.broadcaster = TransformBroadcaster(self, qos=qos_profile)
        self.effector_log_publisher = self.create_publisher(String, '/effector_log', qos_profile)
        self.cable_log_publisher = self.create_publisher(String, '/cable_log', qos_profile)
        self.pulley_log_publisher = self.create_publisher(String, '/pulley_log', qos_profile)

        # SUBSCRIPCIÓN AL TOPIC /VERSION2
        self.coordinates_subscriber = self.create_subscription(
            EffectorCoordinates,
            '/version2',
            self.target_coordinates_callback,
            qos_profile
        )

        # CÁLCULO INICIAL DE LOS PARÁMETROS OBJETIVO
        self.calculate_target_parameters()
        self.get_logger().info("CONTROLADOR ACTIVADO. ESPERANDO COORDENADAS ...")

    # Función calculate_target_parameters()
    # Calcula los parámetros objetivo (longitudes y ángulos de cables y poleas).
    def calculate_target_parameters(self):
        (self.target_left_cable_length, self.target_right_cable_length, self.target_left_cable_angle, self.target_right_cable_angle) = self.calculate_cable_parameters(self.target_x, self.target_y)
        (self.target_left_cable_change, self.target_right_cable_change, self.target_left_pulley_angle, self.target_right_pulley_angle) = self.calculate_pulley_movement(self.initial_x, self.initial_y, self.target_x, self.target_y)

    # Función target_coordinates_callback()
    # Recibe nuevas coordenadas objetivo y reinicia el movimiento del efector.
    def target_coordinates_callback(self, msg):
        if self.objective_achieved:
            self.get_logger().info("OBJETIVO ALCANZADO")
            return
        
        # ACTUALIZACIÓN DE LAS POSICIONES EN CADA MOMENTO
        self.initial_x = msg.current.x
        self.initial_y = msg.current.y
        self.current_x = msg.current.x
        self.current_y = msg.current.y
        self.target_x = msg.target.x
        self.target_y = msg.target.y
        self.moving = True
        self.animation_progress = 0.0
        self.objective_achieved = False
        self.left_pulley_position = 0.0
        self.right_pulley_position = 0.0

        # RECALCULAMIENTO DE TRAYECTORIAS Y PARÁMETROS
        self.calculate_target_parameters()
        self.get_logger().info(f"NUEVA TRAYECTORIA DESDE ({self.initial_x:.3f}, {self.initial_y:.3f}) HASTA ({self.target_x:.3f}, {self.target_y:.3f})")

    # Función calculate_cable_parameters()
    # Calcula longitudes y ángulos de los cables en función de la posición del efector.
    def calculate_cable_parameters(self, x, y):

        # COORDENADAS DE LAS POLEAS
        left_pulley_x = 0.0
        left_pulley_y = self.plane_height
        right_pulley_x = self.plane_width
        right_pulley_y = self.plane_height

        # PUNTOS DE CONEXIÓN DEL EFECTOR
        left_connection_x = x - self.effector_width / 2
        left_connection_y = y + self.effector_height / 2
        right_connection_x = x + self.effector_width / 2
        right_connection_y = y + self.effector_height / 2

        # CÁLCULO DE LONGITUDES DE CADA CABLE
        left_cable_length = math.sqrt((left_connection_x - left_pulley_x)**2 + (left_connection_y - left_pulley_y)**2)
        right_cable_length = math.sqrt((right_connection_x - right_pulley_x)**2 + (right_connection_y - right_pulley_y)**2)
        
        # CÁLCULO DE ÁNGULOS DE CADA CABLE
        left_cable_angle = math.degrees(math.atan2(left_connection_x - left_pulley_x, left_pulley_y - left_connection_y))
        right_cable_angle = math.degrees(math.atan2(right_pulley_x - right_connection_x, right_pulley_y - right_connection_y))
        
        return left_cable_length, right_cable_length, left_cable_angle, right_cable_angle

    # Función calculate_pulley_movement()
    # Calcula la longitud de cable recogida por las poleas en función de la posición del efector.
    def calculate_pulley_movement(self, start_x, start_y, end_x, end_y):
        l1_start, l2_start, a1_start, a2_start = self.calculate_cable_parameters(start_x, start_y)
        l1_end, l2_end, a1_end, a2_end = self.calculate_cable_parameters(end_x, end_y)
        delta_l1 = l1_end - l1_start
        delta_l2 = l2_end - l2_start
        pulley1_angle = delta_l1 / self.pulley_radius
        pulley2_angle = delta_l2 / self.pulley_radius
        return delta_l1, delta_l2, pulley1_angle, pulley2_angle

    # Función check_objective_achieved()
    # Verifica si el efector alcanzó la posición objetivo (con tolerancia).
    def check_objective_achieved(self):
        position_ok = (abs(self.current_x - self.target_x) < 0.005 and abs(self.current_y - self.target_y) < 0.005)
        return position_ok

    # Función control_loop()
    # Actualiza la posición del efector y el estado de las poleas en cada momento.
    def control_loop(self):

        # APAGADO EN CASO DE HABER ALCANZADO EL OBJETIVO
        if self.objective_achieved and not self.shutdown_scheduled:
            self.shutdown_scheduled = True
            self.get_logger().info("CERRANDO CONTROLADOR ...")
            self.create_timer(3.0, self.shutdown_node)
            return
        
        # INTERPOLACIÓN DE POSICIONES EN MOVIMIENTO
        if self.moving and not self.objective_achieved:
            self.animation_progress += 0.02
            if self.animation_progress >= 1.0:
                self.animation_progress = 1.0
                self.moving = False
                self.current_x = self.target_x
                self.current_y = self.target_y
                if self.check_objective_achieved():
                    self.objective_achieved = True
                    self.show_final_summary()
                else:
                    self.get_logger().info("TRAYECTORIA COMPLETADA")

            # INTERPOLACIÓN LINEAL DE LA POSICIÓN
            interpolated_x = self.initial_x + (self.target_x - self.initial_x) * self.animation_progress
            interpolated_y = self.initial_y + (self.target_y - self.initial_y) * self.animation_progress
            
            # CÁLCULO DEL DESPLAZAMIENTO DE CADA POLEA
            if self.animation_progress == 0.02:
                delta_l1, delta_l2, pulley1_angle, pulley2_angle = self.calculate_pulley_movement(self.initial_x, self.initial_y, interpolated_x, interpolated_y)
            else:
                delta_l1, delta_l2, pulley1_angle, pulley2_angle = self.calculate_pulley_movement(self.current_x, self.current_y, interpolated_x, interpolated_y)
            
            # ÁNGULOS ACUMULADOS Y ACTUALIZACIÓN DE ESTADO
            self.left_pulley_position += pulley1_angle
            self.right_pulley_position += pulley2_angle
            self.publish_joint_states()
            self.current_x = interpolated_x
            self.current_y = interpolated_y

    # Función show_final_summary()
    # Muestra un resumen detallado de los resultados finales del movimiento.
    def show_final_summary(self):
        final_left_length, final_right_length, final_left_angle, final_right_angle = self.calculate_cable_parameters(self.current_x, self.current_y)
        initial_left_length, initial_right_length, initial_left_angle, initial_right_angle = self.calculate_cable_parameters(self.initial_x, self.initial_y)
        self.publish_final_status()

        print("═" * 100)
        print("POSICIONES DEL EFECTOR FINAL (X, Y)")
        print(f"• POSICIÓN INICIAL:  ({self.initial_x:.3f}, {self.initial_y:.3f}) m")
        print(f"• POSICIÓN FINAL:    ({self.current_x:.3f}, {self.current_y:.3f}) m")
        print(f"• POSICIÓN OBJETIVO: ({self.target_x:.3f}, {self.target_y:.3f}) m")
        print("")
        print("LONGITUDES DE CADA CABLE (L1, L2)")
        print(f"• LONGITUDES INICIALES:     L1: {initial_left_length:.3f} m, L2: {initial_right_length:.3f} m")
        print(f"• LONGITUDES FINALES:       L1: {final_left_length:.3f} m, L2: {final_right_length:.3f} m")
        print(f"• DIFERENCIA DE LONGITUDES: L1: {self.target_left_cable_change:+.3f} m, L2: {self.target_right_cable_change:+.3f} m")
        print("")
        print("ÁNGULOS DE CADA CABLE (Q1, Q2)")
        print(f"• ÁNGULOS INICIALES:  Q1: {initial_left_angle:.2f} °, Q2: {initial_right_angle:.2f} °")
        print(f"• ÁNGULOS FINALES:    Q1: {final_left_angle:.2f} °, Q2: {final_right_angle:.2f} °")
        print("")
        print("MOVIMIENTO DE CADA POLEA (P1, P2)")
        print(f"• CABLE ELONGADO / RECOGIDO POR P1: {self.target_left_cable_change:+.3f} m")
        print(f"• CABLE ELONGADO / RECOGIDO POR P2: {self.target_right_cable_change:+.3f} m")
        print(f"• ÁNGULO DE GIRO DE P1: {self.target_left_pulley_angle:+.3f} rad ({math.degrees(self.target_left_pulley_angle):+.2f} °)")
        print(f"• ÁNGULO DE GIRO DE P2: {self.target_right_pulley_angle:+.3f} rad ({math.degrees(self.target_right_pulley_angle):+.2f} °)")
        print("═" * 100)

    # Función publish_final_status()
    # Publica los parámetros finales obtenidos en los topics de log.
    def publish_final_status(self):
        final_left_length, final_right_length, final_left_angle, final_right_angle = self.calculate_cable_parameters(self.current_x, self.current_y)
        effector_message = EffectorCoordinates()
        effector_message.current.x = self.current_x
        effector_message.current.y = self.current_y
        effector_message.target.x = self.target_x
        effector_message.target.y = self.target_y
        self.effector_coordinates_publisher.publish(effector_message)
        final_status_message = String()
        final_status_message.data = f"TRAYECTORIA COMPLETADA: ({self.initial_x:.3f}, {self.initial_y:.3f}) → ({self.current_x:.3f}, {self.current_y:.3f})"
        self.effector_log_publisher.publish(final_status_message)
        self.cable_log_publisher.publish(final_status_message)
        self.pulley_log_publisher.publish(final_status_message)

    # Función shutdown_node()
    # Cierra el nodo y detiene su ejecución.
    def shutdown_node(self):
        self.destroy_node()
        rclpy.shutdown()

    # Función publish_effector_parameters()
    # Publica periódicamente las posiciones actual y objetivo del efector.
    def publish_effector_parameters(self):
        if self.objective_achieved:
            return
        effector_message = EffectorCoordinates()
        effector_message.current.x = self.current_x
        effector_message.current.y = self.current_y
        effector_message.target.x = self.target_x
        effector_message.target.y = self.target_y
        self.effector_coordinates_publisher.publish(effector_message)
        effector_log_message = String()
        if self.moving:
            progress_percent = self.animation_progress * 100
            effector_log_message.data = f"EFECTOR: PROGRESO {progress_percent:.1f} % - ACTUAL = ({self.current_x:.3f}, {self.current_y:.3f}) m, OBJETIVO = ({self.target_x:.3f}, {self.target_y:.3f}) m"
        else:
            effector_log_message.data = f"EFECTOR: EN REPOSO - POSICIÓN = ({self.current_x:.3f}, {self.current_y:.3f}) m"
        self.effector_log_publisher.publish(effector_log_message)

    # Función publish_cable_parameters()
    # Publica periódicamente las longitudes y ángulos de los cables.
    def publish_cable_parameters(self):
        if self.objective_achieved:
            return
        current_left_length, current_right_length, current_left_angle, current_right_angle = self.calculate_cable_parameters(self.current_x, self.current_y)
        cable_message = CableParameters()
        cable_message.left_length = current_left_length
        cable_message.right_length = current_right_length
        cable_message.left_angle = current_left_angle
        cable_message.right_angle = current_right_angle
        self.cable_parameters_publisher.publish(cable_message)
        cable_log_message = String()
        cable_log_message.data = f"CABLES: (L1, L2) = ({current_left_length:.3f} m, {current_right_length:.3f} m), (Q1, Q2) =({current_left_angle:.2f} °, {current_right_angle:.2f} °)"
        self.cable_log_publisher.publish(cable_log_message)

    # Función publish_pulley_parameters()
    # Publica periódicamente las longitudes elongadas / recogidas de cable y ángulos de giro de cada polea.
    def publish_pulley_parameters(self):
        if self.objective_achieved:
            return
        if self.moving:
            current_left_cable_change, current_right_cable_change, current_left_pulley_angle, current_right_pulley_angle = self.calculate_pulley_movement(self.initial_x, self.initial_y, self.current_x, self.current_y)
        else:
            current_left_cable_change = 0.0
            current_right_cable_change = 0.0
            current_left_pulley_angle = 0.0
            current_right_pulley_angle = 0.0
        pulley_message = PulleyParameters()
        pulley_message.left_cable_change = current_left_cable_change
        pulley_message.right_cable_change = current_right_cable_change
        pulley_message.left_pulley_angle = current_left_pulley_angle
        pulley_message.right_pulley_angle = current_right_pulley_angle
        self.pulley_parameters_publisher.publish(pulley_message)
        pulley_log_message = String()
        pulley_log_message.data = f"POLEAS: DIFERENCIA = ({current_left_cable_change:+.3f} m, {current_right_cable_change:+.3f} m), ÁNGULO = ({current_left_pulley_angle:+.3f} rad, {current_right_pulley_angle:+.3f} rad)"
        self.pulley_log_publisher.publish(pulley_log_message)

    # Función publish_joint_states()
    # Publica el joint_state de cada polea para su visualización en RVIZ.
    def publish_joint_states(self):
        joint_state_message = JointState()
        joint_state_message.header.stamp = self.get_clock().now().to_msg()
        joint_state_message.name = ['left_wheel_joint', 'right_wheel_joint']
        joint_state_message.position = [self.left_pulley_position, self.right_pulley_position]
        self.joint_state_publisher.publish(joint_state_message)

# Función principal main()
# Punto de entrada del programa.
def main(args=None):
    rclpy.init(args=args)
    controller = Version2Controller()
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