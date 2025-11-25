from abc import ABC, abstractmethod

class Ejercicio(ABC):
    def __init__(self, nombre, descripcion):
        self.__nombre = nombre
        self.__descripcion = descripcion

    @abstractmethod
    def calcular_intensidad(self):
        pass

    @abstractmethod
    def mostrar_instrucciones(self):
        pass

    # --- Getters y Setters ---
    @property
    def nombre(self):
        return self.__nombre

    @property
    def descripcion(self):
        return self.__descripcion