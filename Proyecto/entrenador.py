from db_connection import create_connection
from usuario import Usuario
from plan_entrenamiento import PlanEntrenamiento

class Entrenador(Usuario):
    def __init__(self, id_usuario, nombre, email, especialidad, anos_experiencia):
        super().__init__(id_usuario, nombre, email, 'ENTRENADOR')
        self.especialidad = especialidad
        self.anos_experiencia = anos_experiencia

    @classmethod
    def crear(cls, nombre, email, especialidad, anos_experiencia):
        """Crear un nuevo entrenador"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            # Insertar en usuario
            cursor.execute(
                "INSERT INTO usuario (nombre, email, tipo) VALUES (%s, %s, 'ENTRENADOR')",
                (nombre, email)
            )
            user_id = cursor.lastrowid
            
            # Insertar en entrenador
            cursor.execute(
                "INSERT INTO entrenador (id_usuario, especialidad, anos_experiencia) VALUES (%s, %s, %s)",
                (user_id, especialidad, anos_experiencia)
            )
            conn.commit()
            return cls(user_id, nombre, email, especialidad, anos_experiencia)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_usuario):
        """Buscar entrenador por ID"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.id_usuario, u.nombre, u.email, e.especialidad, e.anos_experiencia 
                FROM usuario u 
                JOIN entrenador e ON u.id_usuario = e.id_usuario 
                WHERE u.id_usuario = %s
            """, (id_usuario,))
            row = cursor.fetchone()
            return cls(row['id_usuario'], row['nombre'], row['email'], row['especialidad'], row['anos_experiencia']) if row else None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        """Listar todos los entrenadores"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.id_usuario, u.nombre, u.email, e.especialidad, e.anos_experiencia 
                FROM usuario u 
                JOIN entrenador e ON u.id_usuario = e.id_usuario 
                ORDER BY u.nombre
            """)
            rows = cursor.fetchall()
            return [cls(row['id_usuario'], row['nombre'], row['email'], row['especialidad'], row['anos_experiencia']) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def crear_plan(self, nombre, objetivo):
        """Crear un nuevo plan de entrenamiento"""
        return PlanEntrenamiento.crear(nombre, objetivo, self.id)

    def obtener_planes(self):
        """Obtener planes creados por el entrenador"""
        return PlanEntrenamiento.buscar_por_entrenador(self.id)

    def obtener_sesiones(self):
        """Obtener sesiones del entrenador"""
        from sesion_entrenamiento import SesionEntrenamiento
        return SesionEntrenamiento.buscar_por_entrenador(self.id)

    def agregar_experiencia(self):
        """Aumentar años de experiencia"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE entrenador SET anos_experiencia = anos_experiencia + 1 WHERE id_usuario = %s",
                (self.id,)
            )
            conn.commit()
            self.anos_experiencia += 1
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def mostrar_dashboard(self):
        """Mostrar dashboard del entrenador"""
        planes = self.obtener_planes()
        sesiones = self.obtener_sesiones()
        
        print(f"--- Panel de Entrenador: {self.nombre} ---")
        print(f"Especialidad: {self.especialidad}")
        print(f"Experiencia: {self.anos_experiencia} años")
        print(f"Planes creados: {len(planes)}")
        print(f"Sesiones programadas: {len(sesiones)}")