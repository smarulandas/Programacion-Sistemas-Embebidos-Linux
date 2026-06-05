from pathlib import Path
import sqlite3
from datetime import datetime


"""
Proyecto: Sistema embebido de portería vehicular

Paso 13:
Gestión manual de vehículos registrados.

Este programa corre en la Raspberry Pi 400 y permite:
- Registrar vehículos nuevos.
- Actualizar vehículos existentes.
- Listar vehículos activos.
- Buscar una placa.
- Desactivar o activar vehículos.

La información se guarda en:
data/porteria.db
"""


# =========================
# Rutas del proyecto
# =========================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "porteria.db"


def conectar_bd():
    """
    Abre conexión con la base de datos SQLite.
    """
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def limpiar_placa(placa):
    """
    Normaliza la placa ingresada por el usuario.

    Ejemplo:
    " abc 123 " -> "ABC123"
    """
    return placa.strip().upper().replace(" ", "").replace("-", "")


def verificar_base_datos():
    """
    Verifica que exista la base de datos antes de usar el programa.
    """
    if not DB_PATH.exists():
        print("[ERROR] No existe la base de datos.")
        print(f"[DETALLE] Ruta esperada: {DB_PATH}")
        print("[SOLUCIÓN] Ejecuta primero: python app/inicializar_bd.py")
        return False

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
          AND name='vehiculos'
    """)

    tabla = cursor.fetchone()
    conexion.close()

    if tabla is None:
        print("[ERROR] No existe la tabla vehiculos.")
        print("[SOLUCIÓN] Ejecuta primero: python app/inicializar_bd.py")
        return False

    return True


def registrar_o_actualizar_vehiculo():
    """
    Registra un vehículo nuevo o actualiza uno existente.

    Si la placa no existe, se crea.
    Si la placa ya existe, se actualizan sus datos y se deja activa.
    """
    print("\n=== Registrar o actualizar vehículo ===")

    placa = limpiar_placa(input("Placa: "))

    if not placa:
        print("[ERROR] La placa no puede estar vacía.")
        return

    tipo_vehiculo = input("Tipo de vehículo, ejemplo CARRO o MOTO: ").strip().upper()
    color = input("Color: ").strip().upper()
    nombre_conductor = input("Nombre del conductor: ").strip()
    celular = input("Celular del conductor: ").strip()

    if not tipo_vehiculo or not color or not nombre_conductor or not celular:
        print("[ERROR] Todos los campos son obligatorios.")
        return

    conexion = conectar_bd()
    cursor = conexion.cursor()

    # Verificar si la placa ya existe
    cursor.execute("""
        SELECT placa
        FROM vehiculos
        WHERE placa = ?
    """, (placa,))

    existe = cursor.fetchone()

    if existe:
        cursor.execute("""
            UPDATE vehiculos
            SET tipo_vehiculo = ?,
                color = ?,
                nombre_conductor = ?,
                celular = ?,
                activo = 1
            WHERE placa = ?
        """, (
            tipo_vehiculo,
            color,
            nombre_conductor,
            celular,
            placa
        ))

        print(f"[OK] Vehículo actualizado y activado: {placa}")

    else:
        cursor.execute("""
            INSERT INTO vehiculos (
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
            placa,
            tipo_vehiculo,
            color,
            nombre_conductor,
            celular,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            1
        ))

        print(f"[OK] Vehículo registrado: {placa}")

    conexion.commit()
    conexion.close()


def listar_vehiculos_activos():
    """
    Lista todos los vehículos activos.
    """
    print("\n=== Vehículos activos ===")

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            placa,
            tipo_vehiculo,
            color,
            nombre_conductor,
            celular,
            fecha_registro
        FROM vehiculos
        WHERE activo = 1
        ORDER BY placa
    """)

    vehiculos = cursor.fetchall()
    conexion.close()

    if not vehiculos:
        print("[INFO] No hay vehículos activos registrados.")
        return

    for vehiculo in vehiculos:
        print("-" * 70)
        print(f"Placa: {vehiculo['placa']}")
        print(f"Tipo: {vehiculo['tipo_vehiculo']}")
        print(f"Color: {vehiculo['color']}")
        print(f"Conductor: {vehiculo['nombre_conductor']}")
        print(f"Celular: {vehiculo['celular']}")
        print(f"Fecha registro: {vehiculo['fecha_registro']}")

    print("-" * 70)


def buscar_vehiculo():
    """
    Busca una placa específica en la base de datos.
    """
    print("\n=== Buscar vehículo ===")

    placa = limpiar_placa(input("Placa a buscar: "))

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            placa,
            tipo_vehiculo,
            color,
            nombre_conductor,
            celular,
            fecha_registro,
            activo
        FROM vehiculos
        WHERE placa = ?
    """, (placa,))

    vehiculo = cursor.fetchone()
    conexion.close()

    if vehiculo is None:
        print(f"[INFO] No existe vehículo con placa {placa}.")
        return

    estado = "ACTIVO" if vehiculo["activo"] == 1 else "INACTIVO"

    print("-" * 70)
    print(f"Placa: {vehiculo['placa']}")
    print(f"Tipo: {vehiculo['tipo_vehiculo']}")
    print(f"Color: {vehiculo['color']}")
    print(f"Conductor: {vehiculo['nombre_conductor']}")
    print(f"Celular: {vehiculo['celular']}")
    print(f"Fecha registro: {vehiculo['fecha_registro']}")
    print(f"Estado: {estado}")
    print("-" * 70)


def cambiar_estado_vehiculo(nuevo_estado):
    """
    Activa o desactiva un vehículo.
    """
    accion = "activar" if nuevo_estado == 1 else "desactivar"

    print(f"\n=== {accion.capitalize()} vehículo ===")

    placa = limpiar_placa(input("Placa: "))

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT placa
        FROM vehiculos
        WHERE placa = ?
    """, (placa,))

    vehiculo = cursor.fetchone()

    if vehiculo is None:
        print(f"[ERROR] No existe vehículo con placa {placa}.")
        conexion.close()
        return

    cursor.execute("""
        UPDATE vehiculos
        SET activo = ?
        WHERE placa = ?
    """, (nuevo_estado, placa))

    conexion.commit()
    conexion.close()

    if nuevo_estado == 1:
        print(f"[OK] Vehículo activado: {placa}")
    else:
        print(f"[OK] Vehículo desactivado: {placa}")


def mostrar_menu():
    """
    Muestra el menú principal.
    """
    print("\n" + "=" * 70)
    print("GESTIÓN DE VEHÍCULOS - PORTERÍA")
    print("=" * 70)
    print("1. Registrar o actualizar vehículo")
    print("2. Listar vehículos activos")
    print("3. Buscar vehículo por placa")
    print("4. Desactivar vehículo")
    print("5. Activar vehículo")
    print("6. Salir")
    print("=" * 70)


def main():
    """
    Ciclo principal del programa.
    """
    if not verificar_base_datos():
        return

    while True:
        mostrar_menu()

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_o_actualizar_vehiculo()

        elif opcion == "2":
            listar_vehiculos_activos()

        elif opcion == "3":
            buscar_vehiculo()

        elif opcion == "4":
            cambiar_estado_vehiculo(0)

        elif opcion == "5":
            cambiar_estado_vehiculo(1)

        elif opcion == "6":
            print("[INFO] Saliendo del gestor de vehículos.")
            break

        else:
            print("[ERROR] Opción no válida.")


if __name__ == "__main__":
    main()