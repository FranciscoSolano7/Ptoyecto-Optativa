from db_connection import create_connection
from datetime import datetime

class SesionEntrenamiento:
    def __init__(self, id_sesion, fecha_hora, cliente, entrenador, plan):
        self.id = id_sesion
        self.fecha_hora = fecha_hora
        self.cliente = cliente
        self.entrenador = entrenador
        self.plan = plan
        self.estado = "PROGRAMADA"
        self.calificacion = 0

    @classmethod
    def crear(cls, fecha_hora, id_cliente, id_entrenador, id_plan):
        """Crear una nueva sesión de entrenamiento"""
        from cliente import Cliente
        from entrenador import Entrenador
        from plan_entrenamiento import PlanEntrenamiento
        
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO sesion_entrenamiento 
                (fecha_hora, id_cliente, id_entrenador, id_plan, estado, calificacion) 
                VALUES (%s, %s, %s, %s, 'PROGRAMADA', 0)""",
                (fecha_hora, id_cliente, id_entrenador, id_plan)
            )
            sesion_id = cursor.lastrowid
            conn.commit()
            
            # Cargar objetos completos
            cliente = Cliente.buscar_por_id(id_cliente)
            entrenador = Entrenador.buscar_por_id(id_entrenador)
            plan = PlanEntrenamiento.buscar_por_id(id_plan)
            
            return cls(sesion_id, fecha_hora, cliente, entrenador, plan)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_sesion):
        """Buscar sesión por ID"""
        from cliente import Cliente
        from entrenador import Entrenador
        from plan_entrenamiento import PlanEntrenamiento
        
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_sesion, fecha_hora, id_cliente, id_entrenador, id_plan, estado, calificacion
                FROM sesion_entrenamiento WHERE id_sesion = %s
            """, (id_sesion,))
            row = cursor.fetchone()
            if not row:
                return None
            
            # Cargar objetos completos
            cliente = Cliente.buscar_por_id(row['id_cliente'])
            entrenador = Entrenador.buscar_por_id(row['id_entrenador'])
            plan = PlanEntrenamiento.buscar_por_id(row['id_plan'])
            
            sesion = cls(row['id_sesion'], row['fecha_hora'], cliente, entrenador, plan)
            sesion.estado = row['estado']
            sesion.calificacion = row['calificacion']
            return sesion
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_cliente(cls, id_cliente):
        """Buscar sesiones por cliente"""
        from cliente import Cliente
        from entrenador import Entrenador
        from plan_entrenamiento import PlanEntrenamiento
        
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_sesion, fecha_hora, id_cliente, id_entrenador, id_plan, estado, calificacion
                FROM sesion_entrenamiento WHERE id_cliente = %s ORDER BY fecha_hora DESC
            """, (id_cliente,))
            rows = cursor.fetchall()
            
            sesiones = []
            for row in rows:
                cliente = Cliente.buscar_por_id(row['id_cliente'])
                entrenador = Entrenador.buscar_por_id(row['id_entrenador'])
                plan = PlanEntrenamiento.buscar_por_id(row['id_plan'])
                
                sesion = cls(row['id_sesion'], row['fecha_hora'], cliente, entrenador, plan)
                sesion.estado = row['estado']
                sesion.calificacion = row['calificacion']
                sesiones.append(sesion)
            
            return sesiones
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_entrenador(cls, id_entrenador):
        """Buscar sesiones por entrenador"""
        from cliente import Cliente
        from entrenador import Entrenador
        from plan_entrenamiento import PlanEntrenamiento
        
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_sesion, fecha_hora, id_cliente, id_entrenador, id_plan, estado, calificacion
                FROM sesion_entrenamiento WHERE id_entrenador = %s ORDER BY fecha_hora DESC
            """, (id_entrenador,))
            rows = cursor.fetchall()
            
            sesiones = []
            for row in rows:
                cliente = Cliente.buscar_por_id(row['id_cliente'])
                entrenador = Entrenador.buscar_por_id(row['id_entrenador'])
                plan = PlanEntrenamiento.buscar_por_id(row['id_plan'])
                
                sesion = cls(row['id_sesion'], row['fecha_hora'], cliente, entrenador, plan)
                sesion.estado = row['estado']
                sesion.calificacion = row['calificacion']
                sesiones.append(sesion)
            
            return sesiones
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def listar_todas(cls):
        """Listar todas las sesiones"""
        from cliente import Cliente
        from entrenador import Entrenador
        from plan_entrenamiento import PlanEntrenamiento
        
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_sesion, fecha_hora, id_cliente, id_entrenador, id_plan, estado, calificacion
                FROM sesion_entrenamiento ORDER BY fecha_hora DESC
            """)
            rows = cursor.fetchall()
            
            sesiones = []
            for row in rows:
                cliente = Cliente.buscar_por_id(row['id_cliente'])
                entrenador = Entrenador.buscar_por_id(row['id_entrenador'])
                plan = PlanEntrenamiento.buscar_por_id(row['id_plan'])
                
                sesion = cls(row['id_sesion'], row['fecha_hora'], cliente, entrenador, plan)
                sesion.estado = row['estado']
                sesion.calificacion = row['calificacion']
                sesiones.append(sesion)
            
            return sesiones
        finally:
            cursor.close()
            conn.close()

    def cambiar_estado(self, nuevo_estado):
        """Cambiar estado de la sesión"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sesion_entrenamiento SET estado = %s WHERE id_sesion = %s",
                (nuevo_estado, self.id)
            )
            conn.commit()
            self.estado = nuevo_estado
            
            # Si se finaliza, agregar al historial
            if nuevo_estado == "FINALIZADA":
                from historial_sesiones import HistorialSesiones
                HistorialSesiones.agregar(self.cliente.id, self.id)
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def calificar(self, calificacion):
        """Calificar la sesión"""
        if 1 <= calificacion <= 5:
            conn = create_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE sesion_entrenamiento SET calificacion = %s WHERE id_sesion = %s",
                    (calificacion, self.id)
                )
                conn.commit()
                self.calificacion = calificacion
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
                conn.close()
        else:
            raise ValueError("La calificación debe ser entre 1 y 5")

    def mostrar_info_participantes(self):
        """Mostrar información de los participantes"""
        return f"Cliente: {self.cliente.nombre} | Entrenador: {self.entrenador.nombre}"

    def eliminar(self):
        """Eliminar sesión"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sesion_entrenamiento WHERE id_sesion = %s", (self.id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()