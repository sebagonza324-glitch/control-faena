"""Creación de conexiones a MySQL."""

import mysql.connector
from mysql.connector.connection import MySQLConnection

from src.config import cargar_configuracion


def get_connection() -> MySQLConnection:
    """Abre una conexión a la base de datos configurada."""
    config = cargar_configuracion()
    return mysql.connector.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
    )


if __name__ == "__main__":
    conexion = get_connection()
    try:
        print("Conexión exitosa a control_faena")
    finally:
        conexion.close()
