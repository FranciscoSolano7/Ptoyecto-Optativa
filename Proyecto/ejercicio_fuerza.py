from ejercicio import Ejercicio

class EjercicioFuerza(Ejercicio):
    def __init__(self, nombre, descripcion, repeticiones, series, peso_kg):
        super().__init__(nombre, descripcion)
        self.__repeticiones = repeticiones
        self.__series = series
        self.__peso_kg = peso_kg

    def calcular_intensidad(self):
        # Volumen de carga total
        return self.__repeticiones * self.__series * self.__peso_kg

    def mostrar_instrucciones(self):
        print(f"Fuerza: {self.__series} series de {self.__repeticiones} reps con {self.__peso_kg}kg.")