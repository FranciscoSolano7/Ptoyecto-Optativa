from usuario import Usuario
# Importación diferida o local para evitar referencias circulares con PlanEntrenamiento si estuvieran en archivos separados
# Aquí asumimos que PlanEntrenamiento se importa o define correctamente

class Entrenador(Usuario):
    def __init__(self, id_usuario, nombre, email, especialidad, anos_experiencia):
        super().__init__(id_usuario, nombre, email)
        self.__especialidad = especialidad
        self.__anos_experiencia = anos_experiencia

    def mostrar_dashboard(self):
        print(f"--- Panel de Entrenador: {self.nombre} ---")
        print(f"Especialidad: {self.__especialidad}")
        print(f"Experiencia: {self.__anos_experiencia} años")

    def crear_plan(self, nombre_plan, objetivo):
        # Nota: Necesitarías importar PlanEntrenamiento aquí
        from plan_entrenamiento import PlanEntrenamiento
        return PlanEntrenamiento(nombre_plan, objetivo)

    def agregar_experiencia(self):
        self.__anos_experiencia += 1