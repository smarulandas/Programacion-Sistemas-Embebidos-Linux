from pathlib import Path
import sqlite3
from datetime import datetime


"""
Proyecto: Sistema embebido de portería vehicular

Paso 15:
Gestión de personas y vehículos asociados.

Permite:
1. Registrar persona y vehículo.
2. Listar personas con sus vehículos.
3. Buscar vehículo por placa.
4. Salir.
"""


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "porteria.db"


def conectar_bd():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def limpiar_texto(texto):
    return texto.strip()


def limpiar_placa(placa):
    return placa.strip().upper().replace(" ", "").replace("-", "")


def verificar_bd():
    if not DB_PATH.exists():
        print("[ERROR] No existe la base de datos.")
        print("[SOLUCIÓN] Ejecuta primero: python app/inicializar_bd.py")
        return False

    return True


def registrar_persona_y_vehiculo():
    print("\n=== Registrar persona y vehículo ===")

    documento = limpiar_texto(input("Documento o identificación: "))
    nombre = limpiar_texto(input("Nombre completo: "))
    celular = limpiar_texto(input("Celular: "))
    tipo_persona = limpiar_texto(input("Tipo de persona, ejemplo ESTUDIANTE, DOCENTE, VISITANTE: ")).upper()

    placa = limpiar_placa(input("Placa del vehículo: "))
    tipo_vehiculo = limpiar_texto(input("Tipo de vehículo, ejemplo CARRO o MOTO: ")).upper()
    color = limpiar_texto(input("Color del vehículo: ")).upper()

    if not documento or not nombre or not celular or not tipo_persona:
        print("[ERROR] Los datos de la persona son obligatorios.")
        return

    if not placa or not tipo_vehiculo or not color:
        print("[ERROR] Los datos del vehículo son obligatorios.")
        return

    conexion = conectar_bd()
    cursor = conexion.cursor()

    # Registrar o actualizar persona
    cursor.execute("""
        SELECT id_persona
        FROM personas
        WHERE documento = ?
    """, (documento,))

    persona = cursor.fetchone()

    if persona is None:
        cursor.execute("""
            INSERT INTO personas (
                documento,
                nombre,
                celular,
                tipo_persona,
                fecha_registro,
                activo
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            documento,
            nombre,
            celular,
            tipo_persona,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            1
        ))

        id_persona = cursor.lastrowid
        print(f"[OK] Persona registrada con id_persona={id_persona}")

    else:
        id_persona = persona["id_persona"]

        cursor.execute("""
            UPDATE personas
            SET nombre = ?,
                celular = ?,
                tipo_persona = ?,
                activo = 1
            WHERE id_persona = ?
        """, (
            nombre,
            celular,
            tipo_persona,
            id_persona
        ))

        print(f"[OK] Persona actualizada con id_persona={id_persona}")

    # Registrar o actualizar vehículo
    cursor.execute("""
        SELECT placa
        FROM vehiculos
        WHERE placa = ?
    """, (placa,))

    vehiculo = cursor.fetchone()

    if vehiculo is None:
        cursor.execute("""
            INSERT INTO vehiculos (
                placa,
                tipo_vehiculo,
                color,
                nombre_conductor,
                celular,
                fecha_registro,
                activo,
                id_persona
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            placa,
            tipo_vehiculo,
            color,
            nombre,
            celular,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            1,
            id_persona
        ))

        print(f"[OK] Vehículo registrado y asociado: {placa}")

    else:
        cursor.execute("""
            UPDATE vehiculos
            SET tipo_vehiculo = ?,
                color = ?,
                nombre_conductor = ?,
                celular = ?,
                activo = 1,
                id_persona = ?
            WHERE placa = ?
        """, (
            tipo_vehiculo,
            color,
            nombre,
            celular,
            id_persona,
            placa
        ))

        print(f"[OK] Vehículo actualizado y asociado: {placa}")

    conexion.commit()
    conexion.close()


def listar_personas_vehiculos():
    print("\n=== Personas y vehículos registrados ===")

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            p.id_persona,
            p.documento,
            p.nombre,
            p.celular,
            p.tipo_persona,
            v.placa,
            v.tipo_vehiculo,
            v.color,
            v.activo
        FROM personas p
        LEFT JOIN vehiculos v
            ON p.id_persona = v.id_persona
        ORDER BY p.nombre, v.placa
    """)

    registros = cursor.fetchall()
    conexion.close()

    if not registros:
        print("[INFO] No hay personas registradas.")
        return

    for fila in registros:
        estado_vehiculo = "ACTIVO" if fila["activo"] == 1 else "INACTIVO"

        print("-" * 70)
        print(f"Persona: {fila['nombre']}")
        print(f"Documento: {fila['documento']}")
        print(f"Celular: {fila['celular']}")
        print(f"Tipo persona: {fila['tipo_persona']}")

        if fila["placa"] is None:
            print("Vehículo: Sin vehículo asociado")
        else:
            print(f"Placa: {fila['placa']}")
            print(f"Tipo vehículo: {fila['tipo_vehiculo']}")
            print(f"Color: {fila['color']}")
            print(f"Estado vehículo: {estado_vehiculo}")

    print("-" * 70)


def buscar_vehiculo_por_placa():
    print("\n=== Buscar vehículo por placa ===")

    placa = limpiar_placa(input("Placa: "))

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            v.placa,
            v.tipo_vehiculo,
            v.color,
            v.activo,
            p.documento,
            p.nombre,
            p.celular,
            p.tipo_persona
        FROM vehiculos v
        LEFT JOIN personas p
            ON v.id_persona = p.id_persona
        WHERE v.placa = ?
    """, (placa,))

    fila = cursor.fetchone()
    conexion.close()

    if fila is None:
        print(f"[INFO] No existe vehículo con placa {placa}.")
        return

    estado = "ACTIVO" if fila["activo"] == 1 else "INACTIVO"

    print("-" * 70)
    print(f"Placa: {fila['placa']}")
    print(f"Tipo vehículo: {fila['tipo_vehiculo']}")
    print(f"Color: {fila['color']}")
    print(f"Estado vehículo: {estado}")
    print(f"Persona asociada: {fila['nombre']}")
    print(f"Documento: {fila['documento']}")
    print(f"Celular: {fila['celular']}")
    print(f"Tipo persona: {fila['tipo_persona']}")
    print("-" * 70)


def mostrar_menu():
    print("\n" + "=" * 70)
    print("GESTIÓN DE PERSONAS Y VEHÍCULOS")
    print("=" * 70)
    print("1. Registrar persona y vehículo")
    print("2. Listar personas con vehículos")
    print("3. Buscar vehículo por placa")
    print("4. Salir")
    print("=" * 70)


def main():
    if not verificar_bd():
        return

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_persona_y_vehiculo()

        elif opcion == "2":
            listar_personas_vehiculos()

        elif opcion == "3":
            buscar_vehiculo_por_placa()

        elif opcion == "4":
            print("[INFO] Saliendo del gestor.")
            break

        else:
            print("[ERROR] Opción no válida.")


if __name__ == "__main__":
    main()
    