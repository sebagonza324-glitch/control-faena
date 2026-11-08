"""Menú de consola para las operaciones de Control Faena."""

from mysql.connector.connection import MySQLConnection


def mostrar_menu(conexion: MySQLConnection) -> None:
    """Muestra opciones para registrar trabajadores y administrar turnos."""
    # TODO: ofrecer registrar trabajador, iniciar turno, registrar salida
    # y ver turnos activos; delegar las operaciones en los repositories.
    raise NotImplementedError
