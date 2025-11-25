from abc import ABC, abstractmethod

class Usuario(ABC):
    def __init__(self, id_usuario, nombre, email):
        self.__id = id_usuario
        self.__nombre = nombre
        self.__email = email

    # Método abstracto
    @abstractmethod
    def mostrar_dashboard(self):
        pass

    # --- Getters y Setters ---
    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, nuevo_nombre):
        self.__nombre = nuevo_nombre

    @property
    def email(self):
        return self.__email
    
    @property
    def id(self):
        return self.__id