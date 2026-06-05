from pathlib import Path
import sqlite3
from datetime import datetime


"""
Proyecto: Sistema embebido de portería vehicular

Paso 12:
Inicialización de la base de datos SQLite.

Este archivo:
- Crea la tabla de vehículos registrados.
- Crea la tabla de eventos de entrada/salida.
- Inserta un vehículo de prueba con placa ABC123.

La base de datos queda en:
data/porteria.db
"""


# Carpeta base del proyecto:
# /home/diseno_digital/proyecto_porteria
BASE_DIR = Path(__file__).resolve().parents[1]

# Carpeta donde guardaremos la base de datos
DATA_DIR = BASE_DIR / "data"

# Ruta del archivo SQLite
DB_PATH = DATA_DIR / "porteria.db"


def crear_tablas():
    """
    Crea las tablas principales del sistema si todavía no existen.
    """

    # Asegura que la carpeta data exista
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    # Tabla de vehículos registrados.
    # Aquí se guarda la información que antes estaba escrita en el código Python.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            placa TEXT PRIMARY KEY,
            tipo_vehiculo TEXT NOT NULL,
            color TEXT NOT NULL,
            nombre_conductor TEXT NOT NULL,
            celular TEXT NOT NULL,
            fecha_registro TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Tabla de eventos.
    # Aquí se guardan las entradas y salidas detectadas.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            evento TEXT NOT NULL,
            placa TEXT NOT NULL,
            estado TEXT NOT NULL,
            contador_esp32 INTEGER,
            origen TEXT,
            detalle TEXT,
            imagen TEXT
        )
    """)

    conexion.commit()
    conexion.close()


def insertar_vehiculo_prueba():
    """
    Inserta el vehículo ABC123 como vehículo registrado.

    Usamos INSERT OR IGNORE para evitar duplicarlo si ejecutamos este archivo
    varias veces.
    """

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO vehiculos (
            placa,
            tipo_vehiculo,
            color,
            nombre_conductor,
            celular,
            fecha_registro,
            activo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "ABC123",
        "CARRO",
        "BLANCO",
        "Conductor de prueba",
        "3000000000",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        1
    ))

    conexion.commit()
    conexion.close()


def mostrar_resumen():
    """
    Muestra un pequeño resumen para confirmar que la base de datos quedó lista.
    """

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM vehiculos")
    total_vehiculos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM eventos")
    total_eventos = cursor.fetchone()[0]

    conexion.close()

    print("=== Base de datos inicializada ===")
    print(f"[OK] Ruta: {DB_PATH}")
    print(f"[OK] Vehículos registrados: {total_vehiculos}")
    print(f"[OK] Eventos registrados: {total_eventos}")


def main():
    crear_tablas()
    insertar_vehiculo_prueba()
    mostrar_resumen()


if __name__ == "__main__":
    main()