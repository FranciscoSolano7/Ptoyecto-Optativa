from datetime import datetime

# Importamos nuestras clases (asumiendo que cada una está en su archivo .py)
from cliente import Cliente
from entrenador import Entrenador
from ejercicio_fuerza import EjercicioFuerza
from ejercicio_cardio import EjercicioCardio
from sesion_entrenamiento import SesionEntrenamiento

def ejecutar_sistema():
    print("=== INICIANDO SISTEMA DE FITNESS ===\n")

    # 1. CREACIÓN DE ACTORES (Usuarios)
    # Instanciamos un Entrenador
    entrenador_juan = Entrenador("E001", "Juan Pérez", "juan@gym.com", "Hipertrofia", 5)
    
    # Instanciamos un Cliente
    cliente_pedro = Cliente("C001", "Pedro López", "pedro@mail.com", "Principiante")

    # Demostración de Polimorfismo: Ambos usan mostrar_dashboard() pero se ve diferente
    entrenador_juan.mostrar_dashboard()
    print("-" * 30)
    cliente_pedro.mostrar_dashboard()
    print("\n")

    # 2. EL ENTRENADOR CREA UN PLAN
    print(f"--- El entrenador {entrenador_juan.nombre} está diseñando un plan ---")
    plan_volumen = entrenador_juan.crear_plan("Volumen Extremo", "Ganancia muscular máxima")

    # 3. CREACIÓN DE EJERCICIOS
    # Creamos un ejercicio de fuerza
    press_banca = EjercicioFuerza("Press de Banca", "Empuje horizontal con barra", 10, 4, 60.5)
    
    # Creamos un ejercicio de cardio
    cinta_correr = EjercicioCardio("Cinta", "Running suave", 20, "CORRER")
    # Usamos el setter para ajustar el ritmo cardiaco
    cinta_correr.duracion_minutos = 25 

    # 4. AGREGAMOS EJERCICIOS AL PLAN (Agregación)
    plan_volumen.agregar_ejercicio(press_banca)
    plan_volumen.agregar_ejercicio(cinta_correr)
    print(f"Plan '{plan_volumen.nombre}' creado con {len(plan_volumen.ejercicios)} ejercicios.\n")

    # 5. PROGRAMAR UNA SESIÓN (Asociación)
    print("--- Programando Sesión de Entrenamiento ---")
    fecha_hoy = datetime.now()
    sesion_1 = SesionEntrenamiento("S100", fecha_hoy, cliente_pedro, entrenador_juan, plan_volumen)
    
    sesion_1.mostrar_info_participantes()
    print(f"Estado inicial: {sesion_1._SesionEntrenamiento__estado}") # Acceso un poco 'trucado' para ver el privado o usamos un getter si lo creaste

    # 6. SIMULAR LA EJECUCIÓN
    print("\n... Entrenando ...")
    sesion_1.cambiar_estado("FINALIZADA")

    # 7. EL CLIENTE CALIFICA Y GUARDA EN HISTORIAL
    print("--- Finalizando y Calificando ---")
    # Intento de calificación inválida
    cliente_pedro.calificar_sesion(sesion_1, 10) 
    # Calificación válida
    cliente_pedro.calificar_sesion(sesion_1, 5)

    # Guardar en el historial del cliente
    cliente_pedro.agregar_sesion_historial(sesion_1)

    print("\n--- Verificando Dashboard del Cliente Actualizado ---")
    cliente_pedro.mostrar_dashboard()

# Esta condición asegura que esto sea lo primero que se ejecute
if __name__ == "__main__":
    ejecutar_sistema()