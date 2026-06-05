from pathlib import Path
import sqlite3
from datetime import datetime


"""
Proyecto: Sistema embebido de portería vehicular

Paso 15:
Migración de base de datos para agregar personas y asociarlas a vehículos.

Este script:
- Crea la tabla personas si no existe.
- Agrega id_persona a vehiculos si no existe.
- Agrega id_persona a eventos si no existe.
- Crea personas iniciales usando los datos antiguos de vehiculos.
- Asocia cada vehículo existente con una persona.
"""


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "porteria.db"


def conectar_bd():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def columna_existe(cursor, tabla, columna):
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [fila["name"] for fila in cursor.fetchall()]
    return columna in columnas


def crear_tabla_personas(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personas (
            id_persona INTEGER PRIMARY KEY AUTOINCREMENT,
            documento TEXT UNIQUE,
            nombre TEXT NOT NULL,
            celular TEXT NOT NULL,
            tipo_persona TEXT NOT NULL,
            fecha_registro TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )
    """)


def agregar_columnas_si_faltan(cursor):
    if not columna_existe(cursor, "vehiculos", "id_persona"):
        cursor.execute("ALTER TABLE vehiculos ADD COLUMN id_persona INTEGER")

    if not columna_existe(cursor, "eventos", "id_persona"):
        cursor.execute("ALTER TABLE eventos ADD COLUMN id_persona INTEGER")


def crear_personas_desde_vehiculos(cursor):
    """
    Toma los vehículos existentes y crea una persona asociada
    si todavía no tienen id_persona.
    """

    cursor.execute("""
        SELECT
            placa,
            nombre_conductor,
            celular,
            id_persona
        FROM vehiculos
    """)

    vehiculos = cursor.fetchall()

    for vehiculo in vehiculos:
        if vehiculo["id_persona"] is not None:
            continue

        nombre = vehiculo["nombre_conductor"] or "Persona sin nombre"
        celular = vehiculo["celular"] or "SIN_CELULAR"

        documento_generado = f"SIN_DOC_{vehiculo['placa']}"

        cursor.execute("""
            INSERT OR IGNORE INTO personas (
                documento,
                nombre,
                celular,
                tipo_persona,
                fecha_registro,
                activo
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            documento_generado,
            nombre,
            celular,
            "SIN_CLASIFICAR",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            1
        ))

        cursor.execute("""
            SELECT id_persona
            FROM personas
            WHERE documento = ?
        """, (documento_generado,))

        persona = cursor.fetchone()

        if persona is not None:
            cursor.execute("""
                UPDATE vehiculos
                SET id_persona = ?
                WHERE placa = ?
            """, (
                persona["id_persona"],
                vehiculo["placa"]
            ))


def mostrar_resumen(cursor):
    cursor.execute("SELECT COUNT(*) AS total FROM personas")
    total_personas = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM vehiculos")
    total_vehiculos = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM vehiculos
        WHERE id_persona IS NOT NULL
    """)
    vehiculos_asociados = cursor.fetchone()["total"]

    print("=== Migración de personas completada ===")
    print(f"[OK] Base de datos: {DB_PATH}")
    print(f"[OK] Personas registradas: {total_personas}")
    print(f"[OK] Vehículos registrados: {total_vehiculos}")
    print(f"[OK] Vehículos asociados a persona: {vehiculos_asociados}")


def main():
    if not DB_PATH.exists():
        print("[ERROR] No existe data/porteria.db")
        print("[SOLUCIÓN] Ejecuta primero: python app/inicializar_bd.py")
        return

    conexion = conectar_bd()
    cursor = conexion.cursor()

    crear_tabla_personas(cursor)
    agregar_columnas_si_faltan(cursor)
    crear_personas_desde_vehiculos(cursor)

    conexion.commit()

    mostrar_resumen(cursor)

    conexion.close()


if __name__ == "__main__":
    main()