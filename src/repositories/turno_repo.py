"""Operaciones de persistencia para turnos."""

from mysql.connector.connection import MySQLConnection


class TrabajadorNoExisteError(Exception):
    """Indica que no existe un trabajador con el RUT solicitado."""


class TurnoYaAbiertoError(Exception):
    """Indica que el trabajador ya tiene un turno activo."""


class TurnoNoActivoError(Exception):
    """Indica que el trabajador no tiene un turno activo para cerrar."""


def iniciar_turno(conexion: MySQLConnection, rut: str) -> int:
    """Abre un turno y devuelve su identificador."""
    # TODO: validar trabajador y turno activo antes de insertar.
    raise NotImplementedError


def registrar_salida(conexion: MySQLConnection, rut: str) -> None:
    """Registra la salida del turno activo del trabajador."""
    # TODO: localizar el turno activo y registrar su salida.
    raise NotImplementedError


def listar_turnos_activos(
    conexion: MySQLConnection,
) -> list[dict[str, object]]:
    """Lista los trabajadores que actualmente tienen un turno activo."""
    # TODO: consultar los inicios sin fila asociada en salida_turno.
    raise NotImplementedError
