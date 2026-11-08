"""Operaciones de persistencia para turnos."""

from mysql.connector.errors import IntegrityError
from mysql.connector.connection import MySQLConnection

from src.db.connection import get_connection


class TrabajadorNoExisteError(Exception):
    """Indica que no existe un trabajador con el RUT solicitado."""


class TurnoYaAbiertoError(Exception):
    """Indica que el trabajador ya tiene un turno activo."""


class TurnoAbiertoError(TurnoYaAbiertoError):
    """Indica que el trabajador ya tiene un turno abierto."""


class TurnoNoActivoError(Exception):
    """Indica que el trabajador no tiene un turno activo para cerrar."""


def obtener_turno_activo(rut: str) -> int | None:
    """Devuelve el identificador del turno abierto, si existe."""
    conexion = get_connection()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT i.id_turno "
            "FROM inicio_turno AS i "
            "LEFT JOIN salida_turno AS s ON s.id_turno = i.id_turno "
            "WHERE i.rut = %s AND s.id_turno IS NULL "
            "LIMIT 1",
            (rut,),
        )
        fila = cursor.fetchone()
        return fila[0] if fila is not None else None
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexion.close()


def iniciar_turno(rut: str) -> int:
    """Abre un turno y devuelve su identificador."""
    if obtener_turno_activo(rut) is not None:
        raise TurnoAbiertoError("El trabajador ya tiene un turno abierto.")

    conexion = get_connection()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO inicio_turno (rut, fecha_inicio) VALUES (%s, NOW())",
            (rut,),
        )
        conexion.commit()
        id_turno = cursor.lastrowid
        if id_turno is None:
            raise RuntimeError("No se pudo obtener el identificador del turno.")
        return id_turno
    except IntegrityError as error:
        if error.errno == 1452:
            raise TrabajadorNoExisteError(
                "No existe un trabajador con el RUT indicado."
            ) from error
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexion.close()


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


if __name__ == "__main__":
    rut_prueba = "11.111.111-1"
    rut_inexistente = "99.999.999-9"

    try:
        print(f"Turno creado: {iniciar_turno(rut_prueba)}")
    except TurnoAbiertoError as error:
        print(error)

    try:
        iniciar_turno(rut_prueba)
    except TurnoAbiertoError as error:
        print(error)

    try:
        iniciar_turno(rut_inexistente)
    except TrabajadorNoExisteError as error:
        print(error)
