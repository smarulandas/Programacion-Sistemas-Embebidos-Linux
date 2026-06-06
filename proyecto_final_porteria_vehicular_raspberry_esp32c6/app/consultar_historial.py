from pathlib import Path
import sqlite3


"""
Proyecto: Sistema embebido de portería vehicular

Paso 17:
Consulta de historial de eventos y estado de vehículos.

Este programa permite revisar:
- Últimos eventos registrados.
- Eventos por placa.
- Vehículos actualmente DENTRO.
- Vehículos actualmente FUERA.
- Alertas registradas.
- Resumen general del sistema.

La información se lee desde:
data/porteria.db
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
    Verifica que exista la base de datos antes de consultar.
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
    """)

    tablas = [fila["name"] for fila in cursor.fetchall()]
    conexion.close()

    tablas_requeridas = ["eventos", "vehiculos", "personas", "estado_vehiculos"]

    for tabla in tablas_requeridas:
        if tabla not in tablas:
            print(f"[ERROR] Falta la tabla: {tabla}")
            print("[SOLUCIÓN] Revisa que hayas ejecutado las migraciones anteriores.")
            return False

    return True


def imprimir_evento(fila):
    """
    Imprime un evento con formato legible.

    En el Paso 22 también muestra la imagen asociada al evento.
    """

    print("-" * 80)
    print(f"ID evento: {fila['id_evento']}")
    print(f"Fecha/hora: {fila['fecha_hora']}")
    print(f"Evento: {fila['evento']}")
    print(f"Placa: {fila['placa']}")
    print(f"Estado: {fila['estado']}")
    print(f"Detalle: {fila['detalle']}")

    if "imagen" in fila.keys():
        imagen = fila["imagen"]

        if imagen is None or imagen == "" or imagen == "SIN_CAMARA":
            print("Imagen: SIN_CAMARA")
        else:
            print(f"Imagen: {imagen}")

    if "nombre" in fila.keys() and fila["nombre"] is not None:
        print(f"Persona: {fila['nombre']}")
        print(f"Documento: {fila['documento']}")
        print(f"Celular: {fila['celular']}")
        print(f"Tipo persona: {fila['tipo_persona']}")


def consultar_ultimos_eventos():
    """
    Muestra los últimos eventos registrados.
    """
    print("\n=== Últimos eventos registrados ===")

    limite_texto = input("Cantidad de eventos a mostrar, ejemplo 10: ").strip()

    if not limite_texto:
        limite = 10
    else:
        try:
            limite = int(limite_texto)
        except ValueError:
            print("[ERROR] Debes escribir un número.")
            return

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            e.id_evento,
            e.fecha_hora,
            e.evento,
            e.placa,
            e.estado,
            e.detalle,
            e.imagen,
            p.nombre,
            p.documento,
            p.celular,
            p.tipo_persona
        FROM eventos e
        LEFT JOIN personas p
            ON e.id_persona = p.id_persona
        ORDER BY e.id_evento DESC
        LIMIT ?
    """, (limite,))

    eventos = cursor.fetchall()
    conexion.close()

    if not eventos:
        print("[INFO] No hay eventos registrados.")
        return

    for evento in eventos:
        imprimir_evento(evento)

    print("-" * 80)


def limpiar_placa(placa):
    """
    Normaliza una placa ingresada por el usuario.
    """
    return placa.strip().upper().replace(" ", "").replace("-", "")


def consultar_eventos_por_placa():
    """
    Muestra todos los eventos asociados a una placa.
    """
    print("\n=== Consultar eventos por placa ===")

    placa = limpiar_placa(input("Ingrese placa: "))

    if not placa:
        print("[ERROR] La placa no puede estar vacía.")
        return

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            e.id_evento,
            e.fecha_hora,
            e.evento,
            e.placa,
            e.estado,
            e.detalle,
            e.imagen,
            p.nombre,
            p.documento,
            p.celular,
            p.tipo_persona
        FROM eventos e
        LEFT JOIN personas p
            ON e.id_persona = p.id_persona
        WHERE e.placa = ?
        ORDER BY e.id_evento DESC
    """, (placa,))

    eventos = cursor.fetchall()
    conexion.close()

    if not eventos:
        print(f"[INFO] No hay eventos registrados para la placa {placa}.")
        return

    for evento in eventos:
        imprimir_evento(evento)

    print("-" * 80)


def consultar_vehiculos_por_estado(estado_buscado):
    """
    Muestra vehículos según estado DENTRO o FUERA.
    """
    print(f"\n=== Vehículos actualmente {estado_buscado} ===")

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            ev.placa,
            ev.estado_actual,
            ev.fecha_hora_entrada,
            ev.ultima_actualizacion,
            v.tipo_vehiculo,
            v.color,
            p.nombre,
            p.documento,
            p.celular,
            p.tipo_persona
        FROM estado_vehiculos ev
        LEFT JOIN vehiculos v
            ON ev.placa = v.placa
        LEFT JOIN personas p
            ON v.id_persona = p.id_persona
        WHERE ev.estado_actual = ?
        ORDER BY ev.placa
    """, (estado_buscado,))

    vehiculos = cursor.fetchall()
    conexion.close()

    if not vehiculos:
        print(f"[INFO] No hay vehículos actualmente {estado_buscado}.")
        return

    for vehiculo in vehiculos:
        print("-" * 80)
        print(f"Placa: {vehiculo['placa']}")
        print(f"Estado actual: {vehiculo['estado_actual']}")
        print(f"Tipo vehículo: {vehiculo['tipo_vehiculo']}")
        print(f"Color: {vehiculo['color']}")
        print(f"Persona: {vehiculo['nombre']}")
        print(f"Documento: {vehiculo['documento']}")
        print(f"Celular: {vehiculo['celular']}")
        print(f"Tipo persona: {vehiculo['tipo_persona']}")

        if estado_buscado == "DENTRO":
            print(f"Fecha/hora entrada: {vehiculo['fecha_hora_entrada']}")

        print(f"Última actualización: {vehiculo['ultima_actualizacion']}")

    print("-" * 80)

def consultar_eventos_con_imagen():
    """
    Muestra únicamente eventos que tienen imagen real asociada.

    Excluye:
    - SIN_CAMARA
    - valores vacíos
    - valores nulos
    """

    print("\n=== Eventos con imagen asociada ===")

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            e.id_evento,
            e.fecha_hora,
            e.evento,
            e.placa,
            e.estado,
            e.detalle,
            e.imagen,
            p.nombre,
            p.documento,
            p.celular,
            p.tipo_persona
        FROM eventos e
        LEFT JOIN personas p
            ON e.id_persona = p.id_persona
        WHERE e.imagen IS NOT NULL
          AND e.imagen != ''
          AND e.imagen != 'SIN_CAMARA'
        ORDER BY e.id_evento DESC
    """)

    eventos = cursor.fetchall()
    conexion.close()

    if not eventos:
        print("[INFO] No hay eventos con imagen asociada.")
        return

    for evento in eventos:
        imprimir_evento(evento)

    print("-" * 80)

def consultar_alertas():
    """
    Muestra eventos que sean alertas o no autorizados.
    """
    print("\n=== Alertas registradas ===")

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            e.id_evento,
            e.fecha_hora,
            e.evento,
            e.placa,
            e.estado,
            e.detalle,
            e.imagen,
            p.nombre,
            p.documento,
            p.celular,
            p.tipo_persona
        FROM eventos e
        LEFT JOIN personas p
            ON e.id_persona = p.id_persona
        WHERE e.estado = 'NO_AUTORIZADO'
           OR e.detalle LIKE '%ALERTA%'
        ORDER BY e.id_evento DESC
    """)

    alertas = cursor.fetchall()
    conexion.close()

    if not alertas:
        print("[INFO] No hay alertas registradas.")
        return

    for alerta in alertas:
        imprimir_evento(alerta)

    print("-" * 80)


def mostrar_resumen_general():
    """
    Muestra un resumen general del sistema.
    """
    print("\n=== Resumen general del sistema ===")

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM personas")
    total_personas = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM vehiculos")
    total_vehiculos = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM eventos")
    total_eventos = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM estado_vehiculos
        WHERE estado_actual = 'DENTRO'
    """)
    total_dentro = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM estado_vehiculos
        WHERE estado_actual = 'FUERA'
    """)
    total_fuera = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM eventos
        WHERE estado = 'NO_AUTORIZADO'
           OR detalle LIKE '%ALERTA%'
    """)
    total_alertas = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM eventos
        WHERE imagen IS NOT NULL
          AND imagen != ''
          AND imagen != 'SIN_CAMARA'
    """)
    total_eventos_con_imagen = cursor.fetchone()["total"]

    conexion.close()

    print("-" * 80)
    print(f"Personas registradas: {total_personas}")
    print(f"Vehículos registrados: {total_vehiculos}")
    print(f"Eventos registrados: {total_eventos}")
    print(f"Vehículos DENTRO: {total_dentro}")
    print(f"Vehículos FUERA: {total_fuera}")
    print(f"Alertas / eventos no autorizados: {total_alertas}")
    print(f"Eventos con imagen asociada: {total_eventos_con_imagen}")
    print("-" * 80)


def mostrar_menu():
    """
    Muestra el menú principal.
    """
    print("\n" + "=" * 80)
    print("CONSULTA DE HISTORIAL - SISTEMA DE PORTERÍA")
    print("=" * 80)
    print("1. Ver últimos eventos")
    print("2. Buscar eventos por placa")
    print("3. Ver vehículos actualmente DENTRO")
    print("4. Ver vehículos actualmente FUERA")
    print("5. Ver alertas registradas")
    print("6. Ver eventos con imagen asociada")
    print("7. Ver resumen general")
    print("8. Salir")
    print("=" * 80)


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
            consultar_ultimos_eventos()

        elif opcion == "2":
            consultar_eventos_por_placa()

        elif opcion == "3":
            consultar_vehiculos_por_estado("DENTRO")

        elif opcion == "4":
            consultar_vehiculos_por_estado("FUERA")

        elif opcion == "5":
            consultar_alertas()

        elif opcion == "6":
            consultar_eventos_con_imagen()

        elif opcion == "7":
            mostrar_resumen_general()

        elif opcion == "8":
            print("[INFO] Saliendo de consulta de historial.")
            break

        else:
            print("[ERROR] Opción no válida.")


if __name__ == "__main__":
    main()