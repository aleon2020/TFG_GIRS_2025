# Shebang que indica que el script debe ejecutarse con el intérprete de Python 3
#!/usr/bin/env python3

# Importación de librerías
import rclpy                                        # Librería de ROS2 para Python
import time                                         # Librería para funciones de tiempo
from rclpy.node import Node                         # Clase base de creación de nodos en ROS2
from rclpy.action import ActionServer               # Servidor para acciones de ROS2
from rclpy.action.server import ServerGoalHandle    # Manejo de goals en el servidor
from tfg_interfaces.action import CountUntil        # Interfaz de acción personalizada

class CountUntilServerNode(Node):
    def __init__(self):

        # Inicialización del nodo con el nombre "count_until_server"
        super().__init__("count_until_server")

        # Creación del Action Server:
        # - self: Referencia al nodo actual.
        # - CountUntil: Tipo de acción que manejará el servidor.
        # - "count_until": Nombre del topic donde se publicará la acción.
        # - execute_callback: Función que se ejecutará cuando llegue un goal.
        self.count_until_server_ = ActionServer(
            self, 
            CountUntil, 
            "count_until", 
            execute_callback=self.execute_callback)
        
        # Mensaje informativo indicando que el servidor está listo
        self.get_logger().info("Action server has been started")
        
    # Callback que se ejecuta cuando un cliente envía un goal
    def execute_callback(self, goal_handle: ServerGoalHandle):
        
        # Extracción de los parámetros de la solicitud (goal)
        # - target_number: Número goal a contar.
        # - period: Período de espera entre números.
        target_number = goal_handle.request.target_number
        period = goal_handle.request.period

        # Mensaje indicando que se comenzará a ejecutar la acción
        self.get_logger().info("Executing the goal")

        # Implementación de la lógica de la acción (contar hasta el número goal)
        counter = 0
        for i in range(target_number):
            counter += 1
            self.get_logger().info(str(counter))    # Log del número actual
            time.sleep(period)                      # Espera el período especificado

        # Una vez completada la acción, se marca el goal como exitoso
        goal_handle.succeed()

        # Creación y envío del resultado de la acción
        result = CountUntil.Result()
        result.reached_number = counter
        return result

# Función principal de inicialización del nodo servidor
def main(args=None):
    rclpy.init(args=args)           # Inicialización del contexto de ROS2
    node = CountUntilServerNode()   # Creación de la instancia del nodo servidor
    rclpy.spin(node)                # Mantiene el nodo activo y procesando eventos / callbacks
    rclpy.shutdown()                # Limpieza y cierre del contexto de ROS2

# Punto de entrada del script
if __name__ == "__main__":
    main()