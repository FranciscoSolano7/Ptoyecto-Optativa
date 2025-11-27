from db_connection import create_connection
from usuario import Usuario

class Cliente(Usuario):
    def __init__(self, id_usuario, nombre, email, nivel_fitness):
        super().__init__(id_usuario, nombre, email, 'CLIENTE')
        self.nivel_fitness = nivel_fitness

    @classmethod
    def crear(cls, nombre, email, nivel_fitness):
        """Crear un nuevo cliente"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            # Insertar en usuario
            cursor.execute(
                "INSERT INTO usuario (nombre, email, tipo) VALUES (%s, %s, 'CLIENTE')",
                (nombre, email)
            )
            user_id = cursor.lastrowid
            
            # Insertar en cliente
            cursor.execute(
                "INSERT INTO cliente (id_usuario, nivel_fitness) VALUES (%s, %s)",
                (user_id, nivel_fitness)
            )
            conn.commit()
            return cls(user_id, nombre, email, nivel_fitness)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_usuario):
        """Buscar cliente por ID"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.id_usuario, u.nombre, u.email, c.nivel_fitness 
                FROM usuario u 
                JOIN cliente c ON u.id_usuario = c.id_usuario 
                WHERE u.id_usuario = %s
            """, (id_usuario,))
            row = cursor.fetchone()
            return cls(row['id_usuario'], row['nombre'], row['email'], row['nivel_fitness']) if row else None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        """Listar todos los clientes"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.id_usuario, u.nombre, u.email, c.nivel_fitness 
                FROM usuario u 
                JOIN cliente c ON u.id_usuario = c.id_usuario 
                ORDER BY u.nombre
            """)
            rows = cursor.fetchall()
            return [cls(row['id_usuario'], row['nombre'], row['email'], row['nivel_fitness']) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def actualizar_nivel(self, nuevo_nivel):
        """Actualizar nivel de fitness del cliente"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE cliente SET nivel_fitness = %s WHERE id_usuario = %s",
                (nuevo_nivel, self.id)
            )
            conn.commit()
            self.nivel_fitness = nuevo_nivel
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def obtener_sesiones(self):
        """Obtener sesiones del cliente"""
        from sesion_entrenamiento import SesionEntrenamiento
        return SesionEntrenamiento.buscar_por_cliente(self.id)

    def calificar_sesion(self, sesion, calificacion):
        """Calificar una sesión de entrenamiento"""
        sesion.calificar(calificacion)

    def agregar_sesion_historial(self, sesion):
        """Agregar sesión al historial del cliente"""
        from historial_sesiones import HistorialSesiones
        HistorialSesiones.agregar(self.id, sesion.id)

    def mostrar_dashboard(self):
        """Mostrar dashboard del cliente"""
        sesiones = self.obtener_sesiones()
        sesiones_completadas = len([s for s in sesiones if s.estado == 'FINALIZADA'])
        
        print(f"--- Dashboard de Cliente: {self.nombre} ---")
        print(f"Nivel: {self.nivel_fitness}")
        print(f"Sesiones completadas: {sesiones_completadas}")
        print(f"Total de sesiones: {len(sesiones)}")