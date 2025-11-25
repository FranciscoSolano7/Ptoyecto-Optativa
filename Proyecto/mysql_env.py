from db_connection import create_connection, close_connection

def main():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES;")
        print("Bases de datos disponibles:")
        for db in cursor:
            print(f" - {db[0]}")
        close_connection(conn)

if __name__ == "__main__":
    main()