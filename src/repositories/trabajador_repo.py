"""Operaciones de persistencia para trabajadores."""

from mysql.connector.errors import IntegrityError

from src.db.connection import get_connection


class RutDuplicadoError(Exception):
    """Indica que ya existe un trabajador con ese RUT."""


def crear_trabajador(rut: str, nombre: str, cargo: str | None = None) -> int:
    """Registra un trabajador y devuelve su identificador."""
    conexion = get_connection()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO trabajador (rut, nombre, cargo) VALUES (%s, %s, %s)",
            (rut, nombre, cargo),
        )
        conexion.commit()
        id_trabajador = cursor.lastrowid
        if id_trabajador is None:
            raise RuntimeError("No se pudo obtener el identificador del trabajador.")
        return id_trabajador
    except IntegrityError as error:
        if error.errno == 1062:
            raise RutDuplicadoError(
                f"Ya existe un trabajador con el RUT {rut}."
            ) from error
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexion.close()


def buscar_por_rut(rut: str) -> dict[str, object] | None:
    """Busca un trabajador por RUT y devuelve sus datos si existe."""
    conexion = get_connection()
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_trabajador, rut, nombre, cargo "
            "FROM trabajador WHERE rut = %s",
            (rut,),
        )
        return cursor.fetchone()
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexion.close()


if __name__ == "__main__":
    rut_prueba = "11.111.111-1"
    try:
        crear_trabajador(rut_prueba, "Prueba", "Operador")
    except RutDuplicadoError as error:
        print(error)

    print(buscar_por_rut(rut_prueba))

    try:
        crear_trabajador(rut_prueba, "Prueba", "Operador")
    except RutDuplicadoError as error:
        print(error)
