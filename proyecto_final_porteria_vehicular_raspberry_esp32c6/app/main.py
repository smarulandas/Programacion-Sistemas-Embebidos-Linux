import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime

import serial

from camara_usb import capturar_imagen_evento


"""
Proyecto: Sistema embebido de portería vehicular

Paso 12:
Aplicación principal de la Raspberry Pi usando SQLite.

Funciones:
- Leer eventos JSON enviados por el ESP32-C6.
- Validar placas contra la base de datos SQLite.
- Responder al ESP32-C6 con AUTORIZADO o NO_AUTORIZADO.
- Guardar cada evento en la tabla eventos.
- Mostrar logs en terminal para verificar el funcionamiento.

La base de datos queda en:
data/porteria.db
"""


# =========================
# Rutas del proyecto
# =========================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "porteria.db"


# =========================
# Configuración serial
# =========================

PUERTO_SERIAL = "/dev/ttyACM0"
BAUDRATE = 115200
TIMEOUT_SEGUNDOS = 1


def conectar_bd():
    """
    Abre conexión con la base de datos SQLite.
    """

    conexion = sqlite3.connect(DB_PATH)

    # Permite acceder a las columnas por nombre, no solo por índice.
    conexion.row_factory = sqlite3.Row

    return conexion

def buscar_vehiculo_por_placa(placa):
    """
    Busca una placa en la tabla vehiculos y trae la persona asociada.

    Retorna:
    - Un registro con datos del vehículo y persona si existe y está activo.
    - None si no existe o está inactivo.
    """

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            v.placa,
            v.tipo_vehiculo,
            v.color,
            v.activo,
            v.id_persona,
            p.documento,
            p.nombre,
            p.celular AS celular_persona,
            p.tipo_persona
        FROM vehiculos v
        LEFT JOIN personas p
            ON v.id_persona = p.id_persona
        WHERE v.placa = ?
          AND v.activo = 1
    """, (placa,))

    vehiculo = cursor.fetchone()

    conexion.close()

    return vehiculo

def obtener_estado_vehiculo(placa):
    """
    Consulta si un vehículo está actualmente DENTRO o FUERA.

    Si por alguna razón no existe registro en estado_vehiculos,
    lo crea automáticamente como FUERA.
    """

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            placa,
            estado_actual,
            id_evento_entrada_actual,
            fecha_hora_entrada,
            ultima_actualizacion
        FROM estado_vehiculos
        WHERE placa = ?
    """, (placa,))

    estado = cursor.fetchone()

    if estado is None:
        cursor.execute("""
            INSERT INTO estado_vehiculos (
                placa,
                estado_actual,
                id_evento_entrada_actual,
                fecha_hora_entrada,
                ultima_actualizacion
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            placa,
            "FUERA",
            None,
            None,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conexion.commit()

        cursor.execute("""
            SELECT
                placa,
                estado_actual,
                id_evento_entrada_actual,
                fecha_hora_entrada,
                ultima_actualizacion
            FROM estado_vehiculos
            WHERE placa = ?
        """, (placa,))

        estado = cursor.fetchone()

    conexion.close()

    return estado


def marcar_vehiculo_dentro(placa, id_evento_entrada):
    """
    Marca un vehículo como DENTRO después de una entrada autorizada.
    """

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE estado_vehiculos
        SET estado_actual = ?,
            id_evento_entrada_actual = ?,
            fecha_hora_entrada = ?,
            ultima_actualizacion = ?
        WHERE placa = ?
    """, (
        "DENTRO",
        id_evento_entrada,
        fecha_actual,
        fecha_actual,
        placa
    ))

    conexion.commit()
    conexion.close()


def marcar_vehiculo_fuera(placa):
    """
    Marca un vehículo como FUERA después de una salida autorizada.
    """

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE estado_vehiculos
        SET estado_actual = ?,
            id_evento_entrada_actual = NULL,
            fecha_hora_entrada = NULL,
            ultima_actualizacion = ?
        WHERE placa = ?
    """, (
        "FUERA",
        fecha_actual,
        placa
    ))

    conexion.commit()
    conexion.close()


def registrar_evento(evento, placa, estado, contador, origen, detalle="", imagen="SIN_CAMARA", id_persona=None):
    """
    Guarda un evento de entrada o salida en la tabla eventos.

    En el Paso 16 también guardamos id_persona cuando la placa
    está asociada a una persona.
    """

    conexion = conectar_bd()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO eventos (
            fecha_hora,
            evento,
            placa,
            estado,
            contador_esp32,
            origen,
            detalle,
            imagen,
            id_persona
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        evento,
        placa,
        estado,
        contador,
        origen,
        detalle,
        imagen,
        id_persona
    ))

    conexion.commit()

    id_evento = cursor.lastrowid

    conexion.close()

    return id_evento


def abrir_puerto_serial():
    """
    Abre el puerto serial donde está conectado el ESP32-C6.
    """

    print("=== Aplicación principal de portería con SQLite ===")
    print(f"[INFO] Base de datos: {DB_PATH}")
    print(f"[INFO] Abriendo puerto serial: {PUERTO_SERIAL}")
    print(f"[INFO] Baudrate: {BAUDRATE}")

    puerto = serial.Serial(
        port=PUERTO_SERIAL,
        baudrate=BAUDRATE,
        timeout=TIMEOUT_SEGUNDOS
    )

    # Espera corta para estabilizar la comunicación serial
    time.sleep(2)

    print("[OK] Puerto serial abierto.")
    print("[INFO] Esperando eventos de portería...\n")

    return puerto


def construir_respuesta(estado, evento, placa):
    """
    Construye la respuesta que se envía al ESP32-C6.

    Ejemplos:
    AUTORIZADO:ENTRADA:ABC123
    NO_AUTORIZADO:SALIDA:XYZ999
    """

    return f"{estado}:{evento}:{placa}\n"


def enviar_respuesta(puerto, respuesta):
    """
    Envía una respuesta al ESP32-C6 por serial.
    """

    puerto.write(respuesta.encode("utf-8"))
    puerto.flush()

    print(f"[RESPUESTA ENVIADA] {respuesta.strip()}")

def limpiar_placa(placa):
    """
    Normaliza la placa ingresada manualmente.

    Ejemplos:
    - " abc 123 " -> "ABC123"
    - "abc-123"   -> "ABC123"
    """
    return placa.strip().upper().replace(" ", "").replace("-", "")


def solicitar_placa_manual(evento):
    """
    Solicita al usuario digitar la placa del vehículo.

    Esta función se usa mientras todavía no tenemos cámara/OCR.
    """
    while True:
        placa = input(f"Ingrese la placa para {evento}: ")
        placa = limpiar_placa(placa)

        if placa:
            return placa

        print("[ERROR] La placa no puede estar vacía.")

def procesar_evento_porteria(puerto, datos):
    """
    Procesa un evento de portería recibido desde el ESP32-C6.

    Lógica Paso 16:
    - ENTRADA solo se autoriza si el vehículo está registrado y está FUERA.
    - SALIDA solo se autoriza si el vehículo está registrado y está DENTRO.
    """

    evento = datos.get("evento", "SIN_EVENTO")
    contador = datos.get("contador", None)
    origen = datos.get("origen", "DESCONOCIDO")

    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "-" * 70)
    print(
        f"[EVENTO RECIBIDO] {fecha_hora} | "
        f"evento={evento} | "
        f"contador={contador}"
    )

    # Captura la imagen inmediatamente cuando llega el evento del ESP32-C6.
    # En este momento todavía no conocemos la placa, por eso usamos PENDIENTE.
    ruta_imagen = capturar_imagen_evento(evento, "PENDIENTE")

    # Luego se solicita la placa manualmente.
    placa = solicitar_placa_manual(evento)

    print(f"[PLACA INGRESADA] {placa}")

    vehiculo = buscar_vehiculo_por_placa(placa)

    # Caso 1: la placa no existe o está inactiva
    if vehiculo is None:
        id_persona = None

        if evento == "SALIDA":
            estado = "NO_AUTORIZADO"
            detalle = "ALERTA: salida de placa no registrada. Posible error de registro de entrada."
            respuesta_evento = "ALERTA_SALIDA_NO_REGISTRADA"
        else:
            estado = "NO_AUTORIZADO"
            detalle = "Placa no registrada o inactiva."
            respuesta_evento = evento

        print("[VALIDACIÓN] Placa no registrada o inactiva.")
        print(f"[ESTADO] {detalle}")

        id_evento = registrar_evento(
            evento=evento,
            placa=placa,
            estado=estado,
            contador=contador,
            origen=origen,
            detalle=detalle,
            imagen=ruta_imagen,
            id_persona=id_persona
        )

        print(f"[BD] Evento guardado con id_evento={id_evento}")

        respuesta = construir_respuesta(estado, respuesta_evento, placa)
        enviar_respuesta(puerto, respuesta)

        print("-" * 70)
        return

    # Caso 2: placa registrada
    id_persona = vehiculo["id_persona"]

    print(
        f"[VALIDACIÓN] Placa registrada | "
        f"tipo={vehiculo['tipo_vehiculo']} | "
        f"color={vehiculo['color']} | "
        f"persona={vehiculo['nombre']} | "
        f"documento={vehiculo['documento']} | "
        f"celular={vehiculo['celular_persona']} | "
        f"tipo_persona={vehiculo['tipo_persona']}"
    )

    estado_vehiculo = obtener_estado_vehiculo(placa)
    estado_actual = estado_vehiculo["estado_actual"]

    print(f"[ESTADO ACTUAL] {placa} está {estado_actual}")

    # Caso 3: ENTRADA
    if evento == "ENTRADA":
        if estado_actual == "FUERA":
            estado = "AUTORIZADO"
            detalle = "Entrada autorizada. Vehículo pasa a estado DENTRO."
            respuesta_evento = "ENTRADA"

            id_evento = registrar_evento(
                evento=evento,
                placa=placa,
                estado=estado,
                contador=contador,
                origen=origen,
                detalle=detalle,
                imagen=ruta_imagen,
                id_persona=id_persona
            )

            marcar_vehiculo_dentro(placa, id_evento)

            print(f"[BD] Evento guardado con id_evento={id_evento}")
            print(f"[CAMBIO ESTADO] {placa}: FUERA -> DENTRO")

        else:
            estado = "NO_AUTORIZADO"
            detalle = "ALERTA: entrada duplicada. El vehículo ya aparece como DENTRO."
            respuesta_evento = "ALERTA_ENTRADA_DUPLICADA"

            id_evento = registrar_evento(
                evento=evento,
                placa=placa,
                estado=estado,
                contador=contador,
                origen=origen,
                detalle=detalle,
                imagen=ruta_imagen,
                id_persona=id_persona
            )

            print(f"[BD] Evento guardado con id_evento={id_evento}")
            print(f"[ALERTA] {detalle}")

    # Caso 4: SALIDA
    elif evento == "SALIDA":
        if estado_actual == "DENTRO":
            estado = "AUTORIZADO"
            detalle = "Salida autorizada. Vehículo pasa a estado FUERA."
            respuesta_evento = "SALIDA"

            id_evento = registrar_evento(
                evento=evento,
                placa=placa,
                estado=estado,
                contador=contador,
                origen=origen,
                detalle=detalle,
                imagen=ruta_imagen,
                id_persona=id_persona
            )

            marcar_vehiculo_fuera(placa)

            print(f"[BD] Evento guardado con id_evento={id_evento}")
            print(f"[CAMBIO ESTADO] {placa}: DENTRO -> FUERA")

        else:
            estado = "NO_AUTORIZADO"
            detalle = "ALERTA: salida sin entrada activa. El vehículo aparece como FUERA."
            respuesta_evento = "ALERTA_SALIDA_SIN_ENTRADA"

            id_evento = registrar_evento(
                evento=evento,
                placa=placa,
                estado=estado,
                contador=contador,
                origen=origen,
                detalle=detalle,
                imagen=ruta_imagen,
                id_persona=id_persona
            )

            print(f"[BD] Evento guardado con id_evento={id_evento}")
            print(f"[ALERTA] {detalle}")

    # Caso 5: evento desconocido
    else:
        estado = "NO_AUTORIZADO"
        detalle = f"Evento no reconocido: {evento}"
        respuesta_evento = "EVENTO_DESCONOCIDO"

        id_evento = registrar_evento(
            evento=evento,
            placa=placa,
            estado=estado,
            contador=contador,
            origen=origen,
            detalle=detalle,
            imagen=ruta_imagen,
            id_persona=id_persona
        )

        print(f"[BD] Evento guardado con id_evento={id_evento}")
        print(f"[ERROR] {detalle}")

    respuesta = construir_respuesta(estado, respuesta_evento, placa)
    enviar_respuesta(puerto, respuesta)

    print("-" * 70)


def procesar_linea(puerto, linea_texto):
    """
    Procesa cada línea recibida por serial.

    Si la línea es JSON:
    - Se intenta interpretar como evento de portería.

    Si no es JSON:
    - Se muestra como log del ESP32-C6.
    """

    linea_texto = linea_texto.strip()

    if not linea_texto:
        return

    if not linea_texto.startswith("{"):
        print(f"[LOG ESP32] {linea_texto}")
        return

    try:
        datos = json.loads(linea_texto)

        tipo = datos.get("tipo", "")

        if tipo == "EVENTO_PORTERIA":
            procesar_evento_porteria(puerto, datos)
        else:
            print(f"[JSON RECIBIDO] {datos}")

    except json.JSONDecodeError:
        print(f"[ADVERTENCIA] JSON inválido: {linea_texto}")


def verificar_base_datos():
    """
    Verifica que la base de datos y las tablas principales existan.
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
          AND name IN ('vehiculos', 'eventos')
    """)

    tablas = [fila["name"] for fila in cursor.fetchall()]

    conexion.close()

    if "vehiculos" not in tablas or "eventos" not in tablas:
        print("[ERROR] Faltan tablas en la base de datos.")
        print("[SOLUCIÓN] Ejecuta primero: python app/inicializar_bd.py")
        return False

    return True


def main():
    """
    Ciclo principal de la aplicación.
    """

    if not verificar_base_datos():
        return

    puerto = None

    try:
        puerto = abrir_puerto_serial()

        while True:
            linea = puerto.readline()
            linea_texto = linea.decode("utf-8", errors="replace")
            procesar_linea(puerto, linea_texto)

    except serial.SerialException as error:
        print("[ERROR] Problema con el puerto serial.")
        print(f"[DETALLE] {error}")
        print("\nPosibles causas:")
        print("- El ESP32-C6 no está conectado.")
        print("- El puerto /dev/ttyACM0 cambió.")
        print("- Otro programa está usando el puerto serial.")

    except KeyboardInterrupt:
        print("\n[INFO] Programa detenido por el usuario.")

    finally:
        if puerto is not None and puerto.is_open:
            puerto.close()
            print("[OK] Puerto serial cerrado.")


if __name__ == "__main__":
    main()