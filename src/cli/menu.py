"""Menú de consola para las operaciones de Control Faena."""

from collections.abc import Callable
from datetime import datetime

from mysql.connector import Error

from src.repositories.trabajador_repo import RutDuplicadoError, crear_trabajador
from src.repositories.turno_repo import (
    SinTurnoAbiertoError,
    TrabajadorNoExisteError,
    TurnoAbiertoError,
    iniciar_turno,
    listar_turnos_activos,
    registrar_salida,
)


def _pedir_valor_obligatorio(etiqueta: str) -> str:
    """Solicita un valor no vacío."""
    while True:
        valor = input(f"{etiqueta}: ").strip()
        if valor:
            return valor
        print(f"Advertencia: {etiqueta} no puede estar vacío.")


def _registrar_trabajador() -> None:
    """Solicita datos y registra un trabajador."""
    rut = _pedir_valor_obligatorio("RUT")
    nombre = _pedir_valor_obligatorio("Nombre")
    cargo = input("Cargo (opcional): ").strip() or None
    id_trabajador = crear_trabajador(rut, nombre, cargo)
    print(f"Trabajador registrado. ID: {id_trabajador}")


def _iniciar_turno() -> None:
    """Solicita un RUT e inicia su turno."""
    rut = _pedir_valor_obligatorio("RUT")
    id_turno = iniciar_turno(rut)
    print(f"Turno iniciado. ID: {id_turno}")


def _registrar_salida() -> None:
    """Solicita un RUT y registra la salida de su turno."""
    rut = _pedir_valor_obligatorio("RUT")
    id_salida = registrar_salida(rut)
    print(f"Salida registrada. ID: {id_salida}")


def _ver_turnos_activos() -> None:
    """Muestra una tabla de los turnos que siguen abiertos."""
    turnos = listar_turnos_activos()
    if not turnos:
        print("No hay turnos activos")
        return

    encabezados = ("RUT", "Nombre", "Cargo", "Fecha de inicio")
    filas: list[tuple[str, str, str, str]] = []
    for turno in turnos:
        fecha_inicio = turno["fecha_inicio"]
        fecha_formateada = (
            fecha_inicio.strftime("%d/%m/%Y %H:%M")
            if isinstance(fecha_inicio, datetime)
            else str(fecha_inicio)
        )
        filas.append(
            (
                str(turno["rut"]),
                str(turno["nombre"]),
                str(turno["cargo"] or ""),
                fecha_formateada,
            )
        )

    anchos = [
        max(len(encabezados[indice]), *(len(fila[indice]) for fila in filas))
        for indice in range(len(encabezados))
    ]
    print(" | ".join(titulo.ljust(anchos[i]) for i, titulo in enumerate(encabezados)))
    print("-+-".join("-" * ancho for ancho in anchos))
    for fila in filas:
        print(" | ".join(valor.ljust(anchos[i]) for i, valor in enumerate(fila)))


def _mostrar_advertencia(error: Exception) -> None:
    """Muestra un aviso claro para errores conocidos."""
    if isinstance(error, RutDuplicadoError):
        print("Advertencia: ya existe un trabajador registrado con ese RUT.")
    elif isinstance(error, TrabajadorNoExisteError):
        print("Advertencia: no existe un trabajador con ese RUT.")
    elif isinstance(error, TurnoAbiertoError):
        print("Advertencia: el trabajador ya tiene un turno abierto.")
    elif isinstance(error, SinTurnoAbiertoError):
        print("Advertencia: el trabajador no tiene un turno abierto.")
    elif isinstance(error, Error):
        print("Hubo un problema con la base de datos. Inténtelo nuevamente.")


def mostrar_menu() -> None:
    """Ejecuta el menú de consola hasta que el usuario salga."""
    opciones: dict[str, Callable[[], None]] = {
        "1": _registrar_trabajador,
        "2": _iniciar_turno,
        "3": _registrar_salida,
        "4": _ver_turnos_activos,
    }

    while True:
        print("\n--- Control Faena ---")
        print("1. Registrar trabajador")
        print("2. Iniciar turno")
        print("3. Registrar salida")
        print("4. Ver turnos activos")
        print("0. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            print("Hasta luego.")
            return

        accion = opciones.get(opcion)
        if accion is None:
            print("Advertencia: opción inválida. Seleccione una opción del menú.")
            continue

        try:
            accion()
        except (
            RutDuplicadoError,
            TrabajadorNoExisteError,
            TurnoAbiertoError,
            SinTurnoAbiertoError,
            Error,
        ) as error:
            _mostrar_advertencia(error)
