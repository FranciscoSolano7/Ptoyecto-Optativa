from db_connection import create_connection
from ejercicio import Ejercicio

class EjercicioCardio(Ejercicio):
    def __init__(self, id_ejercicio, nombre, descripcion, duracion_minutos, tipo_cardio, 
                 nivel_resistencia=1, ritmo_cardiaco_objetivo=120):
        super().__init__(id_ejercicio, nombre, descripcion, 'CARDIO')
        self.duracion_minutos = duracion_minutos
        self.tipo_cardio = tipo_cardio
        self.nivel_resistencia = nivel_resistencia
        self.ritmo_cardiaco_objetivo = ritmo_cardiaco_objetivo

    @classmethod
    def crear(cls, nombre, descripcion, duracion_minutos, tipo_cardio, nivel_resistencia=1, ritmo_cardiaco_objetivo=120):
        """Crear un nuevo ejercicio de cardio"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            # Insertar en ejercicio
            cursor.execute(
                "INSERT INTO ejercicio (nombre, descripcion, tipo) VALUES (%s, %s, 'CARDIO')",
                (nombre, descripcion)
            )
            ejercicio_id = cursor.lastrowid
            
            # Insertar en ejercicio_cardio
            cursor.execute(
                """INSERT INTO ejercicio_cardio (id_ejercicio, duracion_minutos, tipo_cardio, 
                nivel_resistencia, ritmo_cardiaco_objetivo) VALUES (%s, %s, %s, %s, %s)""",
                (ejercicio_id, duracion_minutos, tipo_cardio, nivel_resistencia, ritmo_cardiaco_objetivo)
            )
            conn.commit()
            return cls(ejercicio_id, nombre, descripcion, duracion_minutos, tipo_cardio, 
                      nivel_resistencia, ritmo_cardiaco_objetivo)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_ejercicio):
        """Buscar ejercicio de cardio por ID"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT e.id_ejercicio, e.nombre, e.descripcion, ec.duracion_minutos, 
                       ec.tipo_cardio, ec.nivel_resistencia, ec.ritmo_cardiaco_objetivo 
                FROM ejercicio e 
                JOIN ejercicio_cardio ec ON e.id_ejercicio = ec.id_ejercicio 
                WHERE e.id_ejercicio = %s
            """, (id_ejercicio,))
            row = cursor.fetchone()
            return cls(row['id_ejercicio'], row['nombre'], row['descripcion'], 
                      row['duracion_minutos'], row['tipo_cardio'],
                      row['nivel_resistencia'], row['ritmo_cardiaco_objetivo']) if row else None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        """Listar todos los ejercicios de cardio"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT e.id_ejercicio, e.nombre, e.descripcion, ec.duracion_minutos, 
                       ec.tipo_cardio, ec.nivel_resistencia, ec.ritmo_cardiaco_objetivo 
                FROM ejercicio e 
                JOIN ejercicio_cardio ec ON e.id_ejercicio = ec.id_ejercicio 
                ORDER BY e.nombre
            """)
            rows = cursor.fetchall()
            return [cls(row['id_ejercicio'], row['nombre'], row['descripcion'], 
                       row['duracion_minutos'], row['tipo_cardio'],
                       row['nivel_resistencia'], row['ritmo_cardiaco_objetivo']) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def calcular_intensidad(self):
        """Calcular intensidad del ejercicio"""
        return (self.duracion_minutos * 0.5) + (self.nivel_resistencia * 1.5)

    def mostrar_instrucciones(self):
        """Mostrar instrucciones del ejercicio"""
        return f"Cardio ({self.tipo_cardio}): Mantener por {self.duracion_minutos} min."

    def actualizar_duracion(self, nueva_duracion):
        """Actualizar duración del ejercicio"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE ejercicio_cardio SET duracion_minutos = %s WHERE id_ejercicio = %s", 
                         (nueva_duracion, self.id))
            conn.commit()
            self.duracion_minutos = nueva_duracion
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @property
    def duracion_minutos(self):
        return self._duracion_minutos

    @duracion_minutos.setter
    def duracion_minutos(self, valor):
        self._duracion_minutos = valor