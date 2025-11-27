from db_connection import create_connection
from ejercicio import Ejercicio

class EjercicioFuerza(Ejercicio):
    def __init__(self, id_ejercicio, nombre, descripcion, repeticiones, series, peso_kg):
        super().__init__(id_ejercicio, nombre, descripcion, 'FUERZA')
        self.repeticiones = repeticiones
        self.series = series
        self.peso_kg = peso_kg

    @classmethod
    def crear(cls, nombre, descripcion, repeticiones, series, peso_kg):
        """Crear un nuevo ejercicio de fuerza"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            # Insertar en ejercicio
            cursor.execute(
                "INSERT INTO ejercicio (nombre, descripcion, tipo) VALUES (%s, %s, 'FUERZA')",
                (nombre, descripcion)
            )
            ejercicio_id = cursor.lastrowid
            
            # Insertar en ejercicio_fuerza
            cursor.execute(
                "INSERT INTO ejercicio_fuerza (id_ejercicio, repeticiones, series, peso_kg) VALUES (%s, %s, %s, %s)",
                (ejercicio_id, repeticiones, series, peso_kg)
            )
            conn.commit()
            return cls(ejercicio_id, nombre, descripcion, repeticiones, series, peso_kg)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_ejercicio):
        """Buscar ejercicio de fuerza por ID"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT e.id_ejercicio, e.nombre, e.descripcion, ef.repeticiones, ef.series, ef.peso_kg 
                FROM ejercicio e 
                JOIN ejercicio_fuerza ef ON e.id_ejercicio = ef.id_ejercicio 
                WHERE e.id_ejercicio = %s
            """, (id_ejercicio,))
            row = cursor.fetchone()
            return cls(row['id_ejercicio'], row['nombre'], row['descripcion'], 
                      row['repeticiones'], row['series'], row['peso_kg']) if row else None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        """Listar todos los ejercicios de fuerza"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT e.id_ejercicio, e.nombre, e.descripcion, ef.repeticiones, ef.series, ef.peso_kg 
                FROM ejercicio e 
                JOIN ejercicio_fuerza ef ON e.id_ejercicio = ef.id_ejercicio 
                ORDER BY e.nombre
            """)
            rows = cursor.fetchall()
            return [cls(row['id_ejercicio'], row['nombre'], row['descripcion'], 
                       row['repeticiones'], row['series'], row['peso_kg']) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def calcular_intensidad(self):
        """Calcular intensidad del ejercicio"""
        return self.repeticiones * self.series * self.peso_kg

    def mostrar_instrucciones(self):
        """Mostrar instrucciones del ejercicio"""
        return f"Fuerza: {self.series} series de {self.repeticiones} reps con {self.peso_kg}kg."

    def actualizar(self, repeticiones=None, series=None, peso_kg=None):
        """Actualizar ejercicio de fuerza"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            if repeticiones is not None:
                cursor.execute("UPDATE ejercicio_fuerza SET repeticiones = %s WHERE id_ejercicio = %s", 
                             (repeticiones, self.id))
                self.repeticiones = repeticiones
            if series is not None:
                cursor.execute("UPDATE ejercicio_fuerza SET series = %s WHERE id_ejercicio = %s", 
                             (series, self.id))
                self.series = series
            if peso_kg is not None:
                cursor.execute("UPDATE ejercicio_fuerza SET peso_kg = %s WHERE id_ejercicio = %s", 
                             (peso_kg, self.id))
                self.peso_kg = peso_kg
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()