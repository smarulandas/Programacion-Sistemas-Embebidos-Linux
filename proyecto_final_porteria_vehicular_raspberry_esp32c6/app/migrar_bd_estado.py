from pathlib import Path
import sqlite3
from datetime import datetime


"""
Proyecto: Sistema embebido de portería vehicular

Paso 16:
Migración para controlar el estado DENTRO / FUERA de cada vehículo.

Este script:
- Crea la tabla estado_vehiculos.
- Registra todos los vehículos existentes como FUERA inicialmente.
- No borra datos anteriores.
- No modifica eventos históricos.
"""


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "porteria.db"


def conectar_bd():
    """
    Abre conexión con la base de datos SQLite.
    """
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def verificar_base_datos():
    """
    Verifica que la base de datos exista antes de migrar.
    """
    if not DB_PATH.exists():
        print("[ERROR] No existe la base de datos.")
        print(f"[DETALLE] Ruta esperada: {DB_PATH}")
        print("[SOLUCIÓN] Ejecuta primero: python app/inicializar_bd.py")
        return False

    return True


def crear_tabla_estado_vehiculos(cursor):
    """
    Crea la tabla que guarda el estado actual de cada vehículo.

    estado_actual:
    - FUERA: el vehículo no está dentro del parqueadero.
    - DENTRO: el vehículo tiene una entrada activa.
    """

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estado_vehiculos (
            placa TEXT PRIMARY KEY,
            estado_actual TEXT NOT NULL DEFAULT 'FUERA',
            id_evento_entrada_actual INTEGER,
            fecha_hora_entrada TEXT,
            ultima_actualizacion TEXT NOT NULL,
            FOREIGN KEY (placa) REFERENCES vehiculos(placa)
        )
    """)


def insertar_estados_iniciales(cursor):
    """
    Inserta en estado_vehiculos todos los vehículos existentes.

    Como estamos iniciando esta lógica ahora, todos los vehículos registrados
    se dejan inicialmente como FUERA.
    """

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT OR IGNORE INTO estado_vehiculos (
            placa,
            estado_actual,
            id_evento_entrada_actual,
            fecha_hora_entrada,
            ultima_actualizacion
        )
        SELECT
            placa,
            'FUERA',
            NULL,
            NULL,
            ?
        FROM vehiculos
    """, (fecha_actual,))


def mostrar_resumen(cursor):
    """
    Muestra un resumen de la migración.
    """

    cursor.execute("SELECT COUNT(*) AS total FROM vehiculos")
    total_vehiculos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM estado_vehiculos")
    total_estados = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT estado_actual, COUNT(*) AS total
        FROM estado_vehiculos
        GROUP BY estado_actual
    """)

    estados = cursor.fetchall()

    print("=== Migración de estado DENTRO/FUERA completada ===")
    print(f"[OK] Base de datos: {DB_PATH}")
    print(f"[OK] Vehículos registrados: {total_vehiculos}")
    print(f"[OK] Vehículos con estado creado: {total_estados}")

    for fila in estados:
        print(f"[OK] Estado {fila['estado_actual']}: {fila['total']}")


def main():
    if not verificar_base_datos():
        return

    conexion = conectar_bd()
    cursor = conexion.cursor()

    crear_tabla_estado_vehiculos(cursor)
    insertar_estados_iniciales(cursor)

    conexion.commit()

    mostrar_resumen(cursor)

    conexion.close()


if __name__ == "__main__":
    main()