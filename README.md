# Control Faena

Proyecto de consola en Python 3.11+ para registrar trabajadores y controlar
turnos activos en una faena minera. La persistencia se realizará con MySQL.

## Preparación

1. Crear y activar un entorno virtual.
2. Instalar dependencias con `pip install -r requirements.txt`.
3. Copiar `.env.example` a `.env` y completar las credenciales de MySQL.
4. Crear la base de datos indicada en `MYSQL_DATABASE` y ejecutar
   `src/db/schema.sql`.
5. Iniciar con `python src/main.py`.

El proyecto es un esqueleto: las operaciones de conexión, persistencia y menú
están marcadas con `TODO` o `NotImplementedError`.
