from abc import ABC, abstractmethod
from db_connection import create_connection

class Ejercicio(ABC):
    def __init__(self, id_ejercicio, nombre, descripcion, tipo):
        self.id = id_ejercicio
        self.nombre = nombre
        self.descripcion = descripcion
        self.tipo = tipo

    @abstractmethod
    def calcular_intensidad(self):
        pass

    @abstractmethod
    def mostrar_instrucciones(self):
        pass

    @classmethod
    def crear(cls, nombre, descripcion, tipo):
        """Crear un nuevo ejercicio"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ejercicio (nombre, descripcion, tipo) VALUES (%s, %s, %s)",
                (nombre, descripcion, tipo)
            )
            ejercicio_id = cursor.lastrowid
            conn.commit()
            
            # Retornar instancia del tipo correcto
            if tipo == 'FUERZA':
                from ejercicio_fuerza import EjercicioFuerza
                return EjercicioFuerza.buscar_por_id(ejercicio_id)
            else:  # CARDIO
                from ejercicio_cardio import EjercicioCardio
                return EjercicioCardio.buscar_por_id(ejercicio_id)
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_ejercicio):
        """Buscar ejercicio por ID"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_ejercicio, nombre, descripcion, tipo FROM ejercicio WHERE id_ejercicio = %s",
                (id_ejercicio,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            # Retornar instancia del tipo correcto
            if row['tipo'] == 'FUERZA':
                from ejercicio_fuerza import EjercicioFuerza
                return EjercicioFuerza.buscar_por_id(id_ejercicio)
            else:  # CARDIO
                from ejercicio_cardio import EjercicioCardio
                return EjercicioCardio.buscar_por_id(id_ejercicio)
                
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        """Listar todos los ejercicios"""
        ejercicios = []
        
        # Obtener ejercicios de fuerza
        from ejercicio_fuerza import EjercicioFuerza
        ejercicios.extend(EjercicioFuerza.listar_todos())
        
        # Obtener ejercicios de cardio
        from ejercicio_cardio import EjercicioCardio
        ejercicios.extend(EjercicioCardio.listar_todos())
        
        return sorted(ejercicios, key=lambda x: x.nombre)

    @classmethod
    def buscar_por_nombre(cls, nombre):
        """Buscar ejercicio por nombre"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_ejercicio, tipo FROM ejercicio WHERE nombre = %s",
                (nombre,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            if row['tipo'] == 'FUERZA':
                from ejercicio_fuerza import EjercicioFuerza
                return EjercicioFuerza.buscar_por_id(row['id_ejercicio'])
            else:  # CARDIO
                from ejercicio_cardio import EjercicioCardio
                return EjercicioCardio.buscar_por_id(row['id_ejercicio'])
                
        finally:
            cursor.close()
            conn.close()

    def eliminar(self):
        """Eliminar ejercicio de la base de datos"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ejercicio WHERE id_ejercicio = %s", (self.id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def __str__(self):
        return f"{self.nombre} ({self.tipo}) - {self.descripcion}"