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

    def actualizar_nivel_cliente(self, cliente_id, nuevo_nivel):
        """Actualizar el nivel de fitness de un cliente"""
        from cliente import Cliente
        
        # Verificar que el cliente existe
        cliente = Cliente.buscar_por_id(cliente_id)
        if not cliente:
            raise ValueError("Cliente no encontrado")
        
        # Niveles válidos
        niveles_validos = ["Principiante", "Intermedio", "Avanzado", "Experto"]
        if nuevo_nivel not in niveles_validos:
            raise ValueError(f"Nivel inválido. Debe ser uno de: {', '.join(niveles_validos)}")
        
        # Actualizar en la base de datos
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE cliente SET nivel_fitness = %s WHERE id_usuario = %s",
                (nuevo_nivel, cliente_id)
            )
            conn.commit()
            
            # Actualizar el objeto cliente
            cliente.nivel_fitness = nuevo_nivel
            return cliente
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def obtener_clientes_entrenados(self):
        """Obtener lista de clientes que ha entrenado este entrenador"""
        from cliente import Cliente
        from sesion_entrenamiento import SesionEntrenamiento
        
        # Obtener sesiones donde este entrenador ha trabajado
        sesiones = self.obtener_sesiones()
        
        # Obtener clientes únicos de esas sesiones
        clientes_ids = set(sesion.cliente.id for sesion in sesiones)
        clientes_entrenados = []
        
        for cliente_id in clientes_ids:
            cliente = Cliente.buscar_por_id(cliente_id)
            if cliente:
                clientes_entrenados.append(cliente)
        
        return clientes_entrenados

    def mostrar_dashboard(self):
        """Mostrar dashboard del entrenador"""
        planes = self.obtener_planes()
        sesiones = self.obtener_sesiones()
        
        print(f"--- Panel de Entrenador: {self.nombre} ---")
        print(f"Especialidad: {self.especialidad}")
        print(f"Experiencia: {self.anos_experiencia} años")
        print(f"Planes creados: {len(planes)}")
        print(f"Sesiones programadas: {len(sesiones)}")