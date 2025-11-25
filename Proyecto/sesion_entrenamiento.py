from datetime import datetime

class SesionEntrenamiento:
    def __init__(self, id_sesion, fecha_hora, cliente, entrenador, plan):
        self.__id = id_sesion
        self.__fecha_hora = fecha_hora
        self.__cliente = cliente
        self.__entrenador = entrenador
        self.__plan = plan
        self.__estado = "PROGRAMADA"
        self.__calificacion = 0

    # Setter con validación lógica (Encapsulamiento real)
    @property
    def calificacion(self):
        return self.__calificacion

    @calificacion.setter
    def calificacion(self, valor):
        if 1 <= valor <= 5:
            self.__calificacion = valor
            print(f"Calificación {valor} guardada correctamente.")
        else:
            print("Error: La calificación debe ser entre 1 y 5.")

    def cambiar_estado(self, nuevo_estado):
        self.__estado = nuevo_estado

    def mostrar_info_participantes(self):
        print(f"Cliente: {self.__cliente.nombre} | Entrenador: {self.__entrenador.nombre}")