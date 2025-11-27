from db_connection import create_connection

class Usuario:
    def __init__(self, id_usuario, nombre, email, tipo):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.tipo = tipo

    @classmethod
    def crear(cls, nombre, email, tipo):
        """Crear un nuevo usuario en la base de datos"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuario (nombre, email, tipo) VALUES (%s, %s, %s)",
                (nombre, email, tipo)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return cls(user_id, nombre, email, tipo)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_usuario):
        """Buscar usuario por ID"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_usuario, nombre, email, tipo FROM usuario WHERE id_usuario = %s",
                (id_usuario,)
            )
            row = cursor.fetchone()
            return cls(row['id_usuario'], row['nombre'], row['email'], row['tipo']) if row else None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_email(cls, email):
        """Buscar usuario por email"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_usuario, nombre, email, tipo FROM usuario WHERE email = %s",
                (email,)
            )
            row = cursor.fetchone()
            return cls(row['id_usuario'], row['nombre'], row['email'], row['tipo']) if row else None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        """Listar todos los usuarios"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_usuario, nombre, email, tipo FROM usuario ORDER BY nombre")
            rows = cursor.fetchall()
            return [cls(row['id_usuario'], row['nombre'], row['email'], row['tipo']) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def actualizar(self, nombre=None, email=None):
        """Actualizar información del usuario"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            if nombre:
                cursor.execute("UPDATE usuario SET nombre = %s WHERE id_usuario = %s", (nombre, self.id))
                self.nombre = nombre
            if email:
                cursor.execute("UPDATE usuario SET email = %s WHERE id_usuario = %s", (email, self.id))
                self.email = email
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def eliminar(self):
        """Eliminar usuario de la base de datos"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (self.id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def __str__(self):
        return f"{self.nombre} ({self.email}) - {self.tipo}"