from db_connection import create_connection, close_connection
from datetime import datetime, timedelta

def create_tables(conn):
     # --- Crear tabla usuario ---
    query_usuario = """
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            tipo ENUM('CLIENTE', 'ENTRENADOR') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE = InnoDB;
        """
    
     # --- Crear tabla cliente ---
    query_cliente = """
        CREATE TABLE IF NOT EXISTS cliente (
            id_usuario INT PRIMARY KEY,
            nivel_fitness VARCHAR(50),
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
        ) ENGINE = InnoDB;
        """
    
    # --- Crear tabla entrenador ---
    query_entrenador = """
        CREATE TABLE IF NOT EXISTS entrenador (
            id_usuario INT PRIMARY KEY,
            especialidad VARCHAR(100),
            anos_experiencia INT DEFAULT 0,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
        ) ENGINE = InnoDB;
        """
    
     # --- Crear tabla ejercicio ---
    query_ejercicio = """
        CREATE TABLE IF NOT EXISTS ejercicio (
            id_ejercicio INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT,
            tipo ENUM('FUERZA', 'CARDIO') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE = InnoDB;
        """
    
    # --- Crear tabla ejercicio_fuerza ---
    query_ejercicio_fuerza = """
        CREATE TABLE IF NOT EXISTS ejercicio_fuerza (
            id_ejercicio INT PRIMARY KEY,
            repeticiones INT,
            series INT,
            peso_kg DECIMAL(8,2),
            FOREIGN KEY (id_ejercicio) REFERENCES ejercicio(id_ejercicio) ON DELETE CASCADE
        ) ENGINE = InnoDB;
        """
    
     # --- Crear tabla ejercicio_cardio ---
    query_ejercicio_cardio = """
        CREATE TABLE IF NOT EXISTS ejercicio_cardio (
            id_ejercicio INT PRIMARY KEY,
            duracion_minutos INT,
            tipo_cardio VARCHAR(50),
            nivel_resistencia INT DEFAULT 1,
            ritmo_cardiaco_objetivo INT DEFAULT 120,
            FOREIGN KEY (id_ejercicio) REFERENCES ejercicio(id_ejercicio) ON DELETE CASCADE
        ) ENGINE = InnoDB;
        """
    
     # --- Crear tabla plan_entrenamiento ---
    query_plan_entrenamiento = """
        CREATE TABLE IF NOT EXISTS plan_entrenamiento (
            id_plan INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            objetivo TEXT,
            id_entrenador INT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_entrenador) REFERENCES entrenador(id_usuario)
        ) ENGINE = InnoDB;
        """
    
    # --- Crear tabla plan_ejercicio (TABLA DE RELACIÓN PARA ASIGNAR UN EJERCICIOS A DISTINTOS PLANES DE ENTRENAMIENTO) ---
    query_plan_ejercicio = """
        CREATE TABLE IF NOT EXISTS plan_ejercicio (
            id_plan INT,
            id_ejercicio INT,
            orden INT,
            PRIMARY KEY (id_plan, id_ejercicio),
            FOREIGN KEY (id_plan) REFERENCES plan_entrenamiento(id_plan) ON DELETE CASCADE,
            FOREIGN KEY (id_ejercicio) REFERENCES ejercicio(id_ejercicio) ON DELETE CASCADE
        ) ENGINE = InnoDB;
        """
    
    # --- Crear tabla sesion_entrenamiento ---
    query_sesion_entrenamiento = """
        CREATE TABLE IF NOT EXISTS sesion_entrenamiento (
            id_sesion INT AUTO_INCREMENT PRIMARY KEY,
            fecha_hora DATETIME NOT NULL,
            id_cliente INT NOT NULL,
            id_entrenador INT NOT NULL,
            id_plan INT,
            estado ENUM('PROGRAMADA', 'EN_CURSO', 'FINALIZADA', 'CANCELADA') DEFAULT 'PROGRAMADA',
            calificacion INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_cliente) REFERENCES cliente(id_usuario),
            FOREIGN KEY (id_entrenador) REFERENCES entrenador(id_usuario),
            FOREIGN KEY (id_plan) REFERENCES plan_entrenamiento(id_plan),
            CHECK (calificacion BETWEEN 0 AND 5)
        ) ENGINE = InnoDB;
        """
    
    # --- Crear tabla historial_sesiones ---
    query_historial_sesiones = """
        CREATE TABLE IF NOT EXISTS historial_sesiones (
            id_historial INT AUTO_INCREMENT PRIMARY KEY,
            id_cliente INT NOT NULL,
            id_sesion INT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_cliente) REFERENCES cliente(id_usuario) ON DELETE CASCADE,
            FOREIGN KEY (id_sesion) REFERENCES sesion_entrenamiento(id_sesion) ON DELETE CASCADE
        ) ENGINE = InnoDB;
        """
    
    cursor = conn.cursor()
    cursor.execute(query_usuario)
    print("Se creó la tabla 'usuario'")
    cursor.execute(query_cliente)
    print("Se creó la tabla 'cliente'")
    cursor.execute(query_entrenador)
    print("Se creó la tabla 'entrenador'")
    cursor.execute(query_ejercicio)
    print("Se creó la tabla 'ejercicio'")
    cursor.execute(query_ejercicio_fuerza)
    print("Se creó la tabla 'ejercicio fuerza'")
    cursor.execute(query_ejercicio_cardio)
    print("Se creó la tabla 'ejercicio cardio'")
    cursor.execute(query_plan_entrenamiento)
    print("Se creó la tabla 'plan de entrenamiento'")
    cursor.execute(query_plan_ejercicio)
    print("Se creó la tabla 'plan ejercicio'")
    cursor.execute(query_sesion_entrenamiento)
    print("Se creó la tabla 'sesion de entrenamiento'")
    cursor.execute(query_historial_sesiones)
    print("Se creó la tabla 'historial sesiones'")
    conn.commit()
    cursor.close()

def insert_usuario(conn, nombre, email, tipo):
    query = "INSERT INTO usuario (nombre, email, tipo) VALUES (%s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (nombre, email, tipo))
    conn.commit()
    print(f"Se agregó el usuario: {nombre}")
    cursor.close()

def insert_cliente(conn, id_usuario, nivel_fitness):
    query = "INSERT INTO cliente (id_usuario, nivel_fitness) VALUES (%s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (id_usuario, nivel_fitness))
    conn.commit()
    print(f"Se agregó un cliente nuevo")
    cursor.close()

def insert_entrenador(conn, id_usuario, especialidad, anos_experiencia):
    query = "INSERT INTO entrenador (id_usuario, especialidad, anos_experiencia) VALUES (%s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (id_usuario, especialidad, anos_experiencia))
    conn.commit()
    print(f"Se agregó un entrenador nuevo")
    cursor.close()

def insert_ejercicio(conn, nombre, descripcion, tipo):
    query = "INSERT INTO ejercicio (nombre, descripcion, tipo) VALUES (%s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (nombre, descripcion, tipo))
    conn.commit()
    print(f"Se agregó un ejercicio nuevo")
    cursor.close()

def insert_ejercicio_fuerza(conn, id_ejercicio, repeticiones, series, peso_kg):
    query = "INSERT INTO ejercicio_fuerza (id_ejercicio, repeticiones, series, peso_kg) VALUES (%s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (id_ejercicio, repeticiones, series, peso_kg))
    conn.commit()
    print(f"Se agregó un ejercicio de fuerza nuevo")
    cursor.close()

def insert_ejercicio_cardio(conn, id_ejercicio, duracion_minutos, tipo_cardio):
    query = "INSERT INTO ejercicio_cardio (id_ejercicio, duracion_minutos, tipo_cardio) VALUES (%s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (id_ejercicio, duracion_minutos, tipo_cardio))
    conn.commit()
    print(f"Se agregó un ejercicio de cardio nuevo")
    cursor.close()

def insert_plan_entrenamiento(conn, nombre, objetivo, id_entrenador):
    query = "INSERT INTO plan_entrenamiento (nombre, objetivo, id_entrenador) VALUES (%s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (nombre, objetivo, id_entrenador))
    conn.commit()
    print(f"Se creo nuevo plan de entrenamiento para {objetivo}")
    cursor.close()

def insert_ejercicio_in_plan(conn, id_plan, id_ejercicio, orden):
    query = "INSERT INTO plan_ejercicio (id_plan, id_ejercicio, orden) VALUES (%s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (id_plan, id_ejercicio, orden))
    conn.commit()
    print(f"Se añadio nuevo ejercicio en plan de entrenamiento")
    cursor.close()

def insert_sesion_entrenamiento(conn, fecha_hora, id_cliente, id_entrenador, id_plan, estado, calificacion):
    query = "INSERT INTO sesion_entrenamiento (fecha_hora, id_cliente, id_entrenador, id_plan, estado, calificacion) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (fecha_hora, id_cliente, id_entrenador, id_plan, estado, calificacion))
    conn.commit()
    print(f"nueva sesion programada")
    cursor.close()

def insert_historial_entrenamiento(conn, id_cliente, id_sesion):
    query = "INSERT INTO historial_sesiones (id_cliente, id_sesion) VALUES (%s, %s)"
    cursor = conn.cursor()
    cursor.execute(query, (id_cliente, id_sesion))
    conn.commit()
    print(f"Historial actualizado")
    cursor.close()

def main():
    # Asume que create_connection se modificará o configurará para conectar a la base de datos 'biblioteca'
    conn = create_connection()
    if conn:
        create_tables(conn)

        # Insertar registros en las tablas creadas
        #TABKLA USUARIO
        insert_usuario(conn, "Juan Perez", 'juan@gym.com', 'ENTRENADOR')
        insert_usuario(conn, 'María García', 'maria@gym.com', 'ENTRENADOR')
        insert_usuario(conn, 'Pedro López', 'pedro@mail.com', 'CLIENTE')

        #TABLA CLIENTE
        insert_cliente(conn, 3, 'Principiante')

        #TABLA ENTRENADOR
        insert_entrenador(conn, 1, 'Hipertrofia', 5)
        insert_entrenador(conn, 2, 'Cardio', 3)

        #TABLA EJERCICIO
        insert_ejercicio(conn, 'Press de Banca', 'Empuje horizontal con barra', 'FUERZA')
        insert_ejercicio(conn, 'Sentadillas', 'Ejercicio para piernas', 'FUERZA')
        insert_ejercicio(conn, 'Cinta Correr', 'Running suave', 'CARDIO')

        #TABLA EJERCICIO FUERZA
        insert_ejercicio_fuerza(conn, 1, 10, 4, 60.0)
        insert_ejercicio_fuerza(conn, 2, 12, 3, 70.0)

        #TABLA EJERCICIO CARDIO
        insert_ejercicio_cardio(conn, 3, 30, 'CORRER')

        #TABLA PLAN ENTRENAMIENTO
        insert_plan_entrenamiento(conn, 'Volumen Extremo', 'Ganancia muscular máxima', 1)
        insert_plan_entrenamiento(conn, 'Cardio Intenso', 'Mejora cardiovascular', 2)

        #TABLA EJERCICIO A PLAN
        insert_ejercicio_in_plan(conn, 1, 1, 1)
        insert_ejercicio_in_plan(conn, 1, 2, 2)
        insert_ejercicio_in_plan(conn, 2, 3, 1)

        #TABLA SESION DE ENTRENAMIENTO
        insert_sesion_entrenamiento(conn, datetime.now() + timedelta(days=1), 3, 1, 1, 'PROGRAMADA', 0)
        insert_sesion_entrenamiento(conn, datetime.now() - timedelta(days=1), 3, 1, 1, 'FINALIZADA', 4)

        #TABLA HISTORIAL SESIONES
        insert_historial_entrenamiento(conn, 3, 2)

        print("REGISTROS REALIZADOS")
        close_connection(conn)

if __name__ == "__main__":
    main()