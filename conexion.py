import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def obtener_conexion():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"No se pudo conectar a MySQL: {e}")
        return None