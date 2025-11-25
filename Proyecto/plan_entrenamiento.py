class PlanEntrenamiento:
    def __init__(self, nombre, objetivo):
        self.__nombre = nombre
        self.__objetivo = objetivo
        self.__ejercicios = [] # Lista para agregación

    def agregar_ejercicio(self, ejercicio):
        self.__ejercicios.append(ejercicio)

    @property
    def nombre(self):
        return self.__nombre
    
    @property
    def ejercicios(self):
        return self.__ejercicios