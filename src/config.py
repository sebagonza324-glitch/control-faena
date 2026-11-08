"""Configuración de la aplicación desde variables de entorno."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class DatabaseConfig:
    """Credenciales y datos de conexión a MySQL."""

    host: str
    port: int
    user: str
    password: str
    database: str


def cargar_configuracion() -> DatabaseConfig:
    """Lee la configuración de base de datos desde el entorno."""
    load_dotenv()

    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    if not user:
        raise ValueError("Falta la variable de entorno MYSQL_USER.")
    if not password:
        raise ValueError("Falta la variable de entorno MYSQL_PASSWORD.")

    try:
        port = int(os.getenv("MYSQL_PORT", "3306"))
    except ValueError as error:
        raise ValueError("La variable MYSQL_PORT debe ser un número entero.") from error

    return DatabaseConfig(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=port,
        user=user,
        password=password,
        database=os.getenv("MYSQL_DATABASE", "control_faena"),
    )
