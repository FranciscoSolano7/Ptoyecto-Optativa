from usuario import Usuario

class Cliente(Usuario):
    def __init__(self, id_usuario, nombre, email, nivel_fitness):
        super().__init__(id_usuario, nombre, email)
        self.__nivel_fitness = nivel_fitness
        self.__historial_sesiones = []  # Lista vacía

    def mostrar_dashboard(self):
        print(f"--- Dashboard de Cliente: {self.nombre} ---")
        print(f"Nivel: {self.__nivel_fitness}")
        print(f"Sesiones completadas: {len(self.__historial_sesiones)}")

    def calificar_sesion(self, sesion, calificacion):
        # Llama al setter de la sesión que tiene validación
        sesion.calificacion = calificacion

    def agregar_sesion_historial(self, sesion):
        self.__historial_sesiones.append(sesion)

    # Getter y Setter específico
    @property
    def nivel_fitness(self):
        return self.__nivel_fitness
    
    @nivel_fitness.setter
    def nivel_fitness(self, nuevo_nivel):
        self.__nivel_fitness = nuevo_nivel