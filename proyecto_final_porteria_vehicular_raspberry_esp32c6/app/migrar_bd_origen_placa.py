import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "porteria.db"


def columna_existe(cursor, tabla, columna):
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = cursor.fetchall()

    for info_columna in columnas:
        nombre_columna = info_columna[1]
        if nombre_columna == columna:
            return True

    return False


def agregar_columna_si_no_existe(cursor, tabla, columna, definicion):
    if columna_existe(cursor, tabla, columna):
        print(f"[OK] La columna {columna} ya existe.")
        return

    cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")
    print(f"[OK] Columna creada: {columna}")


def main():
    print("=== Migración: origen de placa ===")
    print(f"[INFO] Base de datos: {DB_PATH}")

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    agregar_columna_si_no_existe(
        cursor,
        "eventos",
        "placa_origen",
        "TEXT DEFAULT 'SIN_REGISTRO'"
    )

    agregar_columna_si_no_existe(
        cursor,
        "eventos",
        "confianza_deteccion",
        "REAL DEFAULT 0.0"
    )

    agregar_columna_si_no_existe(
        cursor,
        "eventos",
        "confianza_ocr",
        "REAL DEFAULT 0.0"
    )

    conexion.commit()
    conexion.close()

    print("[OK] Migración completada.")


if __name__ == "__main__":
    main()