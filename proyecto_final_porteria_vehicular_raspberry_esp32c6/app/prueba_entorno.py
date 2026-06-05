from pathlib import Path
import sqlite3
import sys
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
IMAGES_DIR = BASE_DIR / "imagenes"

DB_PATH = DATA_DIR / "porteria.db"

def verificar_carpetas():
    carpetas = [DATA_DIR, LOGS_DIR, IMAGES_DIR]

    for carpeta in carpetas:
        if carpeta.exists():
            print(f"[OK] Carpeta encontrada: {carpeta}")
        else:
            print(f"[ERROR] No existe la carpeta: {carpeta}")

def probar_sqlite():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prueba_entorno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            mensaje TEXT NOT NULL
        )
    """)

    cursor.execute("""
        INSERT INTO prueba_entorno (fecha_hora, mensaje)
        VALUES (?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Prueba inicial del entorno en Raspberry Pi"
    ))

    conexion.commit()

    cursor.execute("SELECT COUNT(*) FROM prueba_entorno")
    total_registros = cursor.fetchone()[0]

    conexion.close()

    print(f"[OK] SQLite funcionando. Registros en prueba_entorno: {total_registros}")
    print(f"[OK] Base de datos ubicada en: {DB_PATH}")

def main():
    print("=== Prueba inicial del entorno ===")
    print(f"Versión de Python: {sys.version}")
    print(f"Directorio base del proyecto: {BASE_DIR}")

    verificar_carpetas()
    probar_sqlite()

    print("=== Entorno preparado correctamente ===")

if __name__ == "__main__":
    main()
