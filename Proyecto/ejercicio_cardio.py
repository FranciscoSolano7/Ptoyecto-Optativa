from ejercicio import Ejercicio

class EjercicioCardio(Ejercicio):
    def __init__(self, nombre, descripcion, duracion_minutos, tipo_cardio):
        super().__init__(nombre, descripcion)
        self.__duracion_minutos = duracion_minutos
        self.__tipo_cardio = tipo_cardio
        self.__nivel_resistencia = 1 # Valor default
        self.__ritmo_cardiaco_objetivo = 120 # Valor default

    def calcular_intensidad(self):
        return (self.__duracion_minutos * 0.5) + (self.__nivel_resistencia * 1.5)

    def mostrar_instrucciones(self):
        print(f"Cardio ({self.__tipo_cardio}): Mantener por {self.__duracion_minutos} min.")

    # Getters y Setters
    @property
    def duracion_minutos(self):
        return self.__duracion_minutos
    
    @duracion_minutos.setter
    def duracion_minutos(self, valor):
        self.__duracion_minutos = valor