"""Mantenimiento de la base de datos."""

from src.db.connection import get_connection


def limpiar_base_datos() -> None:
    """Elimina los turnos y trabajadores y reinicia sus identificadores."""
    conexion = get_connection()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM salida_turno")
        cursor.execute("DELETE FROM inicio_turno")
        cursor.execute("DELETE FROM trabajador")
        conexion.commit()
        cursor.execute("ALTER TABLE salida_turno AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE inicio_turno AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE trabajador AUTO_INCREMENT = 1")
    except Exception:
        conexion.rollback()
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexion.close()
