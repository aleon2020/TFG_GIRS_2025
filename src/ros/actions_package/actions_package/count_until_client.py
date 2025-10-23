# Shebang que indica que el script debe ejecutarse con el intérprete de Python 3
#!/usr/bin/env python3

# Importación de librerías
import rclpy                                            # Librería de ROS2 para Python
from rclpy.node import Node                             # Clase base de creación de nodos en ROS2
from rclpy.action import ActionClient                   # Cliente para acciones de ROS2
from rclpy.action.client import ClientGoalHandle        # Manejo de goals en el cliente
from interfaces_package.action import CountUntil        # Interfaz de acción personalizada

class CountUntilClientNode(Node):
    def __init__(self):

        # Inicialización del nodo con el nombre "count_until_client"
        super().__init__("count_until_client")

        # Creación del Action Client:
        # - self: Referencia al nodo actual.
        # - CountUntil: Tipo de acción que manejará el cliente.
        # - "count_until": Nombre del topic donde se publicará la acción.
        self.count_until_client_ = ActionClient(
            self, 
            CountUntil, 
            "count_until")

    # Método para enviar un goal al Action Server
    def send_goal(self, target_number, period):
        
        # Espera a que el Action Server esté disponible
        self.count_until_client_.wait_for_server()

        # Creación del mensaje del goal
        goal = CountUntil.Goal()

        # Establecimiento del número goal
        goal.target_number = target_number

        # Establecimiento del período de espera
        goal.period = period

        # Envío asíncrono del goal al servidor:
        # - send_goal_async: Envía el goal y retorna uno futurible.
        # - add_done_callback: Registra un callback para cuando llegue la respuesta.
        self.get_logger().info("Sending goal")
        self.count_until_client_. \
            send_goal_async(goal). \
            add_done_callback(self.goal_response_callback)

    # Callback que se ejecuta cuando el servidor responde al goal enviado
    def goal_response_callback(self, future):

        # future.result: Obtiene el resultado de la operación asíncrona.
        self.goal_handle_: ClientGoalHandle = future.result()

        # Verifica si el servidor aceptó el objetivo: Si fue aceptado, solicita el resultado
        # de forma asíncrona y registra un callback para cuando el resultado esté disponible.
        if self.goal_handle_.accepted:
            self.goal_handle_.get_result_async().add_done_callback(self.goal_result_callback)

    # Callback que se ejecuta cuando el servidor envía el resultado final
    def goal_result_callback(self, future):

        # future.result: Obtiene el resultado de la acción.
        result = future.result().result

        # Log del resultado recibido del servidor
        self.get_logger().info("Result: " + str(result.reached_number))

# Función principal de inicialización del nodo cliente
def main(args=None):
    rclpy.init(args=args)           # Inicialización del contexto de ROS2
    node = CountUntilClientNode()   # Creación de la instancia del nodo cliente
    node.send_goal(6, 1.0)          # Envío del goal al servidor con parámetros específicos
    rclpy.spin(node)                # Mantiene el nodo activo y procesando eventos / callbacks
    rclpy.shutdown()                # Limpieza y cierre del contexto de ROS2

# Punto de entrada del script
if __name__ == "__main__":
    main()