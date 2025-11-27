from db_connection import create_connection

class PlanEntrenamiento:
    def __init__(self, id_plan, nombre, objetivo, id_entrenador):
        self.id_plan = id_plan
        self.nombre = nombre
        self.objetivo = objetivo
        self.id_entrenador = id_entrenador
        self.ejercicios = []

    @classmethod
    def crear(cls, nombre, objetivo, id_entrenador):
        """Crear un nuevo plan de entrenamiento"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO plan_entrenamiento (nombre, objetivo, id_entrenador) VALUES (%s, %s, %s)",
                (nombre, objetivo, id_entrenador)
            )
            plan_id = cursor.lastrowid
            conn.commit()
            return cls(plan_id, nombre, objetivo, id_entrenador)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_id(cls, id_plan):
        """Buscar plan por ID"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_plan, nombre, objetivo, id_entrenador FROM plan_entrenamiento WHERE id_plan = %s",
                (id_plan,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            
            plan = cls(row['id_plan'], row['nombre'], row['objetivo'], row['id_entrenador'])
            plan.cargar_ejercicios()
            return plan
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def buscar_por_entrenador(cls, id_entrenador):
        """Buscar planes por entrenador"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_plan, nombre, objetivo, id_entrenador FROM plan_entrenamiento WHERE id_entrenador = %s",
                (id_entrenador,)
            )
            rows = cursor.fetchall()
            planes = []
            for row in rows:
                plan = cls(row['id_plan'], row['nombre'], row['objetivo'], row['id_entrenador'])
                plan.cargar_ejercicios()
                planes.append(plan)
            return planes
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def listar_todos(cls):
        """Listar todos los planes"""
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_plan, nombre, objetivo, id_entrenador FROM plan_entrenamiento ORDER BY nombre")
            rows = cursor.fetchall()
            planes = []
            for row in rows:
                plan = cls(row['id_plan'], row['nombre'], row['objetivo'], row['id_entrenador'])
                plan.cargar_ejercicios()
                planes.append(plan)
            return planes
        finally:
            cursor.close()
            conn.close()

    def cargar_ejercicios(self):
        """Cargar ejercicios del plan"""
        from ejercicio import Ejercicio
        conn = create_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT pe.id_ejercicio, pe.orden 
                FROM plan_ejercicio pe 
                WHERE pe.id_plan = %s 
                ORDER BY pe.orden
            """, (self.id_plan,))
            rows = cursor.fetchall()
            
            self.ejercicios = []
            for row in rows:
                ejercicio = Ejercicio.buscar_por_id(row['id_ejercicio'])
                if ejercicio:
                    self.ejercicios.append(ejercicio)
        finally:
            cursor.close()
            conn.close()

    def agregar_ejercicio(self, ejercicio, orden=None):
        """Agregar ejercicio al plan"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            
            # Obtener el siguiente orden si no se especifica
            if orden is None:
                cursor.execute("SELECT COALESCE(MAX(orden), 0) + 1 FROM plan_ejercicio WHERE id_plan = %s", 
                             (self.id_plan,))
                orden = cursor.fetchone()[0]
            
            cursor.execute(
                "INSERT INTO plan_ejercicio (id_plan, id_ejercicio, orden) VALUES (%s, %s, %s)",
                (self.id_plan, ejercicio.id, orden)
            )
            conn.commit()
            self.ejercicios.append(ejercicio)
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def eliminar_ejercicio(self, ejercicio):
        """Eliminar ejercicio del plan"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM plan_ejercicio WHERE id_plan = %s AND id_ejercicio = %s",
                (self.id_plan, ejercicio.id)
            )
            conn.commit()
            self.ejercicios = [e for e in self.ejercicios if e.id != ejercicio.id]
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def actualizar(self, nombre=None, objetivo=None):
        """Actualizar información del plan"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            if nombre:
                cursor.execute("UPDATE plan_entrenamiento SET nombre = %s WHERE id_plan = %s", 
                             (nombre, self.id_plan))
                self.nombre = nombre
            if objetivo:
                cursor.execute("UPDATE plan_entrenamiento SET objetivo = %s WHERE id_plan = %s", 
                             (objetivo, self.id_plan))
                self.objetivo = objetivo
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def eliminar(self):
        """Eliminar plan de entrenamiento"""
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM plan_entrenamiento WHERE id_plan = %s", (self.id_plan,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def __str__(self):
        return f"{self.nombre} - {self.objetivo} ({len(self.ejercicios)} ejercicios)"