"""Operaciones de persistencia para turnos."""

from mysql.connector.errors import IntegrityError

from src.db.connection import get_connection


class TrabajadorNoExisteError(Exception):
    """Indica que no existe un trabajador con el RUT solicitado."""


class TurnoYaAbiertoError(Exception):
    """Indica que el trabajador ya tiene un turno activo."""


class TurnoAbiertoError(TurnoYaAbiertoError):
    """Indica que el trabajador ya tiene un turno abierto."""


class TurnoNoActivoError(Exception):
    """Indica que el trabajador no tiene un turno activo para cerrar."""


class SinTurnoAbiertoError(TurnoNoActivoError):
    """Indica que no hay un turno abierto para registrar la salida."""


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


def registrar_salida(rut: str) -> int:
    """Registra la salida del turno activo del trabajador."""
    id_turno = obtener_turno_activo(rut)
    if id_turno is None:
        raise SinTurnoAbiertoError(
            "El trabajador no tiene un turno abierto para registrar la salida."
        )

    conexion = get_connection()
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO salida_turno (id_turno, fecha_salida) VALUES (%s, NOW())",
            (id_turno,),
        )
        conexion.commit()
        id_salida = cursor.lastrowid
        if id_salida is None:
            raise RuntimeError("No se pudo obtener el identificador de la salida.")
        return id_salida
    except IntegrityError as error:
        if error.errno == 1062:
            raise SinTurnoAbiertoError(
                "El turno ya tiene una salida registrada."
            ) from error
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexion.close()


def listar_turnos_activos() -> list[dict[str, object]]:
    """Lista los trabajadores que actualmente tienen un turno activo."""
    conexion = get_connection()
    cursor = None
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT t.rut, t.nombre, t.cargo, i.fecha_inicio "
            "FROM inicio_turno i "
            "JOIN trabajador t ON i.rut = t.rut "
            "LEFT JOIN salida_turno s ON i.id_turno = s.id_turno "
            "WHERE s.fecha_salida IS NULL "
            "ORDER BY i.fecha_inicio;"
        )
        return cursor.fetchall()
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexion.close()


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

    try:
        print("Salida registrada:", registrar_salida(rut_prueba))
    except SinTurnoAbiertoError as error:
        print(error)

    try:
        registrar_salida(rut_prueba)
    except SinTurnoAbiertoError as error:
        print(error)

    iniciar_turno(rut_prueba)
    print("Turnos activos:", listar_turnos_activos())
    registrar_salida(rut_prueba)
    print("Turnos activos después de la salida:", listar_turnos_activos())
