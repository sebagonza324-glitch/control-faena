"""Operaciones de persistencia para trabajadores."""

from mysql.connector.connection import MySQLConnection


class RutDuplicadoError(Exception):
    """Indica que ya existe un trabajador con ese RUT."""


def crear_trabajador(
    conexion: MySQLConnection,
    rut: str,
    nombre: str,
    cargo: str | None = None,
) -> None:
    """Registra un trabajador; puede generar RutDuplicadoError."""
    # TODO: insertar usando una consulta SQL parametrizada.
    raise NotImplementedError


def buscar_por_rut(
    conexion: MySQLConnection,
    rut: str,
) -> dict[str, object] | None:
    """Busca un trabajador por RUT y devuelve sus datos si existe."""
    # TODO: consultar con parámetros y retornar el registro encontrado.
    raise NotImplementedError
