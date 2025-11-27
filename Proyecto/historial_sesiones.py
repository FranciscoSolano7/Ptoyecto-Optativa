from db_connection import create_connection

class HistorialSesiones:
    def __init__(self, id_historial, id_cliente, id_sesion, fecha_registro):
        self.id_historial = id_historial
        self.id_cliente = id_cliente
        self.id_sesion = id_sesion
        self.fecha_registro = fecha_registro

    @classmethod
    def agregar(cls, id_cliente, id_sesion):
        """Agregar sesión al historial"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO historial_sesiones (id_cliente, id_sesion) VALUES (%s, %s)",
                (id_cliente, id_sesion)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_cliente(cls, id_cliente):
        """Buscar historial por cliente"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT h.id_historial, h.id_cliente, h.id_sesion, h.fecha_registro,
                       s.fecha_hora, s.estado, s.calificacion
                FROM historial_sesiones h
                JOIN sesion_entrenamiento s ON h.id_sesion = s.id_sesion
                WHERE h.id_cliente = %s
                ORDER BY h.fecha_registro DESC
            """, (id_cliente,))
            rows = cursor.fetchall()
            return [cls(row['id_historial'], row['id_cliente'], row['id_sesion'], row['fecha_registro']) 
                    for row in rows]
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def listar_todo(cls):
        """Listar todo el historial"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_historial, id_cliente, id_sesion, fecha_registro
                FROM historial_sesiones
                ORDER BY fecha_registro DESC
            """)
            rows = cursor.fetchall()
            return [cls(row['id_historial'], row['id_cliente'], row['id_sesion'], row['fecha_registro']) 
                    for row in rows]
        finally:
            cursor.close()
            conn.close()