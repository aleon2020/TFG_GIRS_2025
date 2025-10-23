# Implementación de un robot por cables para el control
# de un efector final en diversas tareas.

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile
import math
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from tf2_ros import TransformBroadcaster

try:
    from interfaces_package.msg import EffectorPath as EffectorPathMsg
except Exception:
    EffectorPathMsg = None

try:
    from interfaces_package.msg import EffectorCoordinates as EffectorCoordinatesMsg
except Exception:
    EffectorCoordinatesMsg = None

from interfaces_package.msg import CableParameters, PulleyParameters, EffectorCoordinates as EffectorCoordinatesOut

# COMPILACIÓN, ENLAZADO Y EJECUCIÓN
# TERMINAL 1: colcon build --symlink-install
# TERMINAL 2: ros2 run robot_package version3_controller
# TERMINAL 3: ros2 topic echo /effector_coordinates
# TERMINAL 4: ros2 topic echo /cable_parameters
# TERMINAL 5: ros2 topic echo /pulley_parameters
# TERMINAL 6: ros2 topic echo /effector_log
# TERMINAL 7: ros2 topic echo /cable_log
# TERMINAL 8: ros2 topic echo /pulley_log
# TERMINAL 9: 
# ros2 topic pub --once /version3 interfaces_package/msg/EffectorPath "
# points_number: 7
# points:
# - {x: 0.30, y: 0.50}
# - {x: 0.40, y: 0.70}
# - {x: 0.60, y: 0.70}
# - {x: 0.70, y: 0.50}
# - {x: 0.60, y: 0.30}
# - {x: 0.40, y: 0.30}
# - {x: 0.30, y: 0.50}
# "

class Version3Controller(Node):

    # Función __init__()
    # Inicializa el nodo, define parámetros del sistema y configura publicadores y subscriptores.
    def __init__(self):
        super().__init__('version3_controller')

        # PARÁMETROS GEOMÉTRICOS DEL SISTEMA
        self.plane_width = 1.0
        self.plane_height = 1.0
        self.effector_width = 0.1
        self.effector_height = 0.1
        self.pulley_radius = 0.05

        # VARIABLES DE POSICIÓN Y ESTADO
        self.current_x = 0.5
        self.current_y = 0.5
        self.points = []
        self.points_number = 0
        self.segment_index = 0
        self.moving = False
        self.animation_progress = 0.0
        self.objective_achieved = False
        self.shutdown_scheduled = False

        # ESTADO Y POSICIONES INICIALES Y FINALES DE LAS POLEAS
        self.left_pulley_position = 0.0
        self.right_pulley_position = 0.0
        self.initial_x = self.current_x
        self.initial_y = self.current_y
        self.target_x = self.current_x
        self.target_y = self.current_y
        self.segment_target_params = []

        # TIMERS DE CONTROL PARA PUBLICACIONES PERIÓDICAS
        self.control_timer = self.create_timer(0.1, self.control_loop)
        self.effector_timer = self.create_timer(0.25, self.publish_effector_parameters)
        self.cable_timer = self.create_timer(0.25, self.publish_cable_parameters)
        self.pulley_timer = self.create_timer(0.25, self.publish_pulley_parameters)

        # CONFIGURACIÓN DE LA COMUNICACIÓN QOS
        qos_profile = QoSProfile(depth=10)
        self.effector_coordinates_publisher = self.create_publisher(EffectorCoordinatesOut, '/effector_coordinates', qos_profile)
        self.cable_parameters_publisher = self.create_publisher(CableParameters, '/cable_parameters', qos_profile)
        self.pulley_parameters_publisher = self.create_publisher(PulleyParameters, '/pulley_parameters', qos_profile)
        self.joint_state_publisher = self.create_publisher(JointState, 'joint_states', qos_profile)
        self.broadcaster = TransformBroadcaster(self, qos=qos_profile)
        self.effector_log_publisher = self.create_publisher(String, '/effector_log', qos_profile)
        self.cable_log_publisher = self.create_publisher(String, '/cable_log', qos_profile)
        self.pulley_log_publisher = self.create_publisher(String, '/pulley_log', qos_profile)

        # SUBSCRIPCIÓN AL TOPIC /VERSION3
        if EffectorPathMsg is not None:
            self.coordinates_subscriber = self.create_subscription(EffectorPathMsg, '/version3', self.path_callback, qos_profile)
        elif EffectorCoordinatesMsg is not None:
            self.coordinates_subscriber = self.create_subscription(EffectorCoordinatesMsg, '/version3', self.path_callback, qos_profile)
        else:
            self.coordinates_subscriber = self.create_subscription(EffectorCoordinatesOut, '/version3', self.path_callback, qos_profile)
        self.get_logger().info("CONTROLADOR ACTIVADO. ESPERANDO COORDENADAS ...")

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

    # Función path_callback()
    # Procesa el mensaje recibido con una trayectoria (lista de puntos) y configura el recorrido.
    def path_callback(self, msg):
        if self.objective_achieved:
            self.get_logger().info("OBJETIVO ALCANZADO")
            return
        points_number = getattr(msg, 'points_number', None)
        if points_number is None:
            points_number = 0
        points_list = []
        if hasattr(msg, 'points') and isinstance(getattr(msg, 'points'), (list, tuple)):
            for p in msg.points:
                points_list.append((float(p.x), float(p.y)))
        if not points_list:
            for i in range(1, 11):
                for prefix in ('point', 'punto', 'point', 'pt'):
                    attr = f"{prefix}{i}"
                    if hasattr(msg, attr):
                        p = getattr(msg, attr)
                        try:
                            x = float(p.x)
                            y = float(p.y)
                        except Exception:
                            try:
                                x = float(p['x'])
                                y = float(p['y'])
                            except Exception:
                                continue
                        points_list.append((x, y))
                        break
        if points_number is None or points_number == 0:
            points_number = len(points_list)
        else:
            points_number = int(points_number)
        if points_number < 3:
            self.get_logger().error(f"SE REQUIEREN COMO MÍNIMO {points_number} PUNTOS")
            return
        if points_number > 10:
            self.get_logger().error(f"SE REQUIEREN COMO MÁXIMO {points_number} PUNTOS")
            points_number = 10
        if len(points_list) < points_number:
            self.get_logger().error(f"SE ESPERABAN {points_number} PUNTOS PERO SOLO SE RECIBIERON {len(points_list)}")
            return
        self.points = [(float(px), float(py)) for (px, py) in points_list[:points_number]]
        self.points_number = points_number
        self.segment_index = 0
        self.initial_x, self.initial_y = self.points[0]
        self.current_x, self.current_y = self.initial_x, self.initial_y
        self.target_x, self.target_y = self.points[1]
        self.moving = True
        self.animation_progress = 0.0
        self.objective_achieved = False
        self.shutdown_scheduled = False
        self.left_pulley_position = 0.0
        self.right_pulley_position = 0.0
        self.segment_target_params = []
        for i in range(self.points_number - 1):
            sx, sy = self.points[i]
            ex, ey = self.points[i+1]
            l1, l2, a1, a2 = self.calculate_cable_parameters(ex, ey)
            delta_l1, delta_l2, p1_angle, p2_angle = self.calculate_pulley_movement(sx, sy, ex, ey)
            self.segment_target_params.append({
                'start': (sx, sy),
                'end': (ex, ey),
                'end_lengths': (l1, l2),
                'delta_l': (delta_l1, delta_l2),
                'pulley_angles': (p1_angle, p2_angle)
            })
        self.get_logger().info(f"NUEVA TRAYECTORIA RECIBIDA DE {self.points_number} PUNTOS")
        self.get_logger().info("DESPLAZAMIENTO DESDE EL PUNTO 1 HASTA EL PUNTO 2")

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
                self.current_x = self.target_x
                self.current_y = self.target_y
                delta_l1, delta_l2, pulley1_angle, pulley2_angle = self.calculate_pulley_movement(self.initial_x, self.initial_y, self.current_x, self.current_y)
                self.left_pulley_position += pulley1_angle
                self.right_pulley_position += pulley2_angle
                self.publish_joint_states()
                if self.segment_index < (self.points_number - 2):
                    self.segment_index += 1
                    self.initial_x, self.initial_y = self.points[self.segment_index]
                    self.target_x, self.target_y = self.points[self.segment_index + 1]
                    self.animation_progress = 0.0
                    self.get_logger().info(f"DESPLAZAMIENTO DESDE EL PUNTO {self.segment_index+1} HASTA EL PUNTO {self.segment_index+2}")
                else:
                    if self.check_objective_achieved():
                        self.objective_achieved = True
                        self.moving = False
                        self.show_final_summary()
                    else:
                        self.get_logger().info("TRAYECTORIA COMPLETADA")
                        self.moving = False
                return
            
            # INTERPOLACIÓN LINEAL DE LA POSICIÓN
            interpolated_x = self.initial_x + (self.target_x - self.initial_x) * self.animation_progress
            interpolated_y = self.initial_y + (self.target_y - self.initial_y) * self.animation_progress
            
            # CÁLCULO DEL DESPLAZAMIENTO DE CADA POLEA
            delta_l1, delta_l2, pulley1_angle, pulley2_angle = self.calculate_pulley_movement(self.current_x, self.current_y, interpolated_x, interpolated_y)
            
            # ÁNGULOS ACUMULADOS Y ACTUALIZACIÓN DE ESTADO
            self.left_pulley_position += pulley1_angle
            self.right_pulley_position += pulley2_angle
            self.publish_joint_states()
            self.current_x = interpolated_x
            self.current_y = interpolated_y

    # Función publish_effector_parameters()
    # Publica periódicamente las posiciones actual y objetivo del efector.
    def publish_effector_parameters(self):
        if self.objective_achieved:
            return
        effector_message = EffectorCoordinatesOut()
        effector_message.current.x = self.current_x
        effector_message.current.y = self.current_y
        effector_message.target.x = self.target_x
        effector_message.target.y = self.target_y
        self.effector_coordinates_publisher.publish(effector_message)
        effector_log_message = String()
        if self.moving:
            progress_percent = self.animation_progress * 100
            effector_log_message.data = (f"EFECTOR: PROGRESO DEL SEGMENTO [{self.segment_index+1}/{max(1,self.points_number-1)}] "
                                         f"{progress_percent:.1f}% - POSICIÓN ACTUAL = ({self.current_x:.3f}, {self.current_y:.3f}), "
                                         f"POSICIÓN OBJETIVO = ({self.target_x:.3f}, {self.target_y:.3f})")
        else:
            effector_log_message.data = f"EFECTOR: EN REPOSO - POSICIÓN = ({self.current_x:.3f}, {self.current_y:.3f})"
        self.effector_log_publisher.publish(effector_log_message)

    # Función publish_cable_parameters()
    # Publica periódicamente las longitudes y ángulos de los cables.
    def publish_cable_parameters(self):
        if self.objective_achieved:
            return
        current_left_length, current_right_length, current_left_angle, current_right_angle = self.calculate_cable_parameters(self.current_x, self.current_y)
        cable_msg = CableParameters()
        cable_msg.left_length = current_left_length
        cable_msg.right_length = current_right_length
        cable_msg.left_angle = current_left_angle
        cable_msg.right_angle = current_right_angle
        self.cable_parameters_publisher.publish(cable_msg)
        cable_log_message = String()
        cable_log_message.data = f"CABLES: (L1, L2) = ({current_left_length:.3f} m, {current_right_length:.3f} m), (Q1, Q2) =({current_left_angle:.2f} °, {current_right_angle:.2f} °)"
        self.cable_log_publisher.publish(cable_log_message)

    # Función publish_pulley_parameters()
    # Publica periódicamente las longitudes elongadas / recogidas de cable y ángulos de giro de cada polea.
    def publish_pulley_parameters(self):
        if self.objective_achieved:
            return
        if self.moving:
            seg_start_x, seg_start_y = self.initial_x, self.initial_y
            current_left_cable_change, current_right_cable_change, current_left_pulley_angle, current_right_pulley_angle = \
                self.calculate_pulley_movement(seg_start_x, seg_start_y, self.current_x, self.current_y)
        else:
            current_left_cable_change = 0.0
            current_right_cable_change = 0.0
            current_left_pulley_angle = 0.0
            current_right_pulley_angle = 0.0
        pulley_msg = PulleyParameters()
        pulley_msg.left_cable_change = current_left_cable_change
        pulley_msg.right_cable_change = current_right_cable_change
        pulley_msg.left_pulley_angle = current_left_pulley_angle
        pulley_msg.right_pulley_angle = current_right_pulley_angle
        self.pulley_parameters_publisher.publish(pulley_msg)
        pulley_log_message = String()
        pulley_log_message.data = (f"POLEAS: SEGMENTO [{self.segment_index+1}/{max(1,self.points_number-1)}] "
                                   f"DIFERENCIA = ({current_left_cable_change:+.3f} m, {current_right_cable_change:+.3f} m), "
                                   f"ÁNGULOS = ({current_left_pulley_angle:+.3f} rad, {current_right_pulley_angle:+.3f} rad)")
        self.pulley_log_publisher.publish(pulley_log_message)

    # Función publish_joint_states()
    # Publica el joint_state de cada polea para su visualización en RVIZ.
    def publish_joint_states(self):
        joint_state_message = JointState()
        joint_state_message.header.stamp = self.get_clock().now().to_msg()
        joint_state_message.name = ['left_wheel_joint', 'right_wheel_joint']
        joint_state_message.position = [self.left_pulley_position, self.right_pulley_position]
        self.joint_state_publisher.publish(joint_state_message)

    def show_final_summary(self):
        print("═" * 100)
        print(f"NÚMERO DE PUNTOS: {self.points_number}")
        print("\nPUNTOS POR LOS QUE HA PASADO EL EFECTOR")
        for i, (x, y) in enumerate(self.points):
            print(f"• {i+1:02d}: ({x:.3f}, {y:.3f}) m")
        for i, (x, y) in enumerate(self.points):
            L1, L2, q1, q2 = self.calculate_cable_parameters(x, y)
            print(f"\nDATOS POSICIÓN NÚMERO {i+1}")
            print(f"• L1 = {L1:.3f} m, L2 = {L2:.3f} m")
            print(f"• Q1 = {q1:.2f} °, Q2 = {q2:.2f} °")
        for i in range(self.points_number - 1):
            sx, sy = self.points[i]
            ex, ey = self.points[i+1]
            L1_i, L2_i, _, _ = self.calculate_cable_parameters(sx, sy)
            L1_f, L2_f, _, _ = self.calculate_cable_parameters(ex, ey)
            L1_mov = L1_f - L1_i
            L2_mov = L2_f - L2_i
            P1_mov_rad = L1_mov / self.pulley_radius
            P2_mov_rad = L2_mov / self.pulley_radius
            print(f"\nMOVIMIENTO DE CADA POLEA ENTRE LAS POSICIONES {i+1} Y {i+2}")
            print(f"• ΔL1 = {L1_mov:+.3f} m, ΔL2 = {L2_mov:+.3f} m")
            print(f"• P1 = {P1_mov_rad:+.3f} rad ({math.degrees(P1_mov_rad):+.2f} °)")
            print(f"• P2 = {P2_mov_rad:+.3f} rad ({math.degrees(P2_mov_rad):+.2f} °)")
        print("═" * 100)
        self.publish_final_status()

    # Función publish_final_status()
    # Publica los parámetros finales obtenidos en los topics de log.
    def publish_final_status(self):
        final_left_length, final_right_length, final_left_angle, final_right_angle = self.calculate_cable_parameters(self.current_x, self.current_y)
        effector_message = EffectorCoordinatesOut()
        effector_message.current.x = self.current_x
        effector_message.current.y = self.current_y
        effector_message.target.x = self.target_x
        effector_message.target.y = self.target_y
        self.effector_coordinates_publisher.publish(effector_message)
        final_status_message = String()
        final_status_message.data = f"TRAYECTORIA COMPLETADA: {self.segment_index+1} SEGMENTOS RECORRIDOS DE {max(1, self.points_number-1)}"
        self.effector_log_publisher.publish(final_status_message)
        self.cable_log_publisher.publish(final_status_message)
        self.pulley_log_publisher.publish(final_status_message)

    # Función shutdown_node()
    # Cierra el nodo y detiene su ejecución.
    def shutdown_node(self):
        self.destroy_node()
        rclpy.shutdown()

# Función principal main()
# Punto de entrada del programa.
def main(args=None):
    rclpy.init(args=args)
    controller = Version3Controller()
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