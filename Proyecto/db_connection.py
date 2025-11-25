import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()  # Cargar las variables del archivo .env

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if connection.is_connected():
            print("Conexión exitosa a MySQL")
            return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None

def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        print("Conexión cerrada.")