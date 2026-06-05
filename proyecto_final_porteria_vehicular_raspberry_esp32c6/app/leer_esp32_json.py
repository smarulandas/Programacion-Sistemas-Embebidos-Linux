import json
import time
from datetime import datetime

import serial


"""
Proyecto: Sistema embebido de portería vehicular

Paso 8:
Este programa corre en la Raspberry Pi 400 y lee por comunicación serial
los mensajes enviados por el ESP32-C6.

En el Paso 7, el ESP32-C6 empezó a enviar mensajes JSON como:

{"origen":"ESP32C6","evento":"PING","contador":0,"rgb":"ROJO"}

Este programa:
- Abre el puerto serial /dev/ttyACM0.
- Lee línea por línea.
- Ignora mensajes que no sean JSON.
- Decodifica los mensajes JSON válidos.
- Muestra en pantalla el evento, contador y color RGB recibido.
"""


# Puerto serial donde la Raspberry detectó el ESP32-C6
PUERTO_SERIAL = "/dev/ttyACM0"

# Velocidad del monitor serial del ESP32-C6.
# Esta velocidad es independiente de la velocidad de flasheo.
BAUDRATE = 115200

# Tiempo máximo de espera para leer una línea
TIMEOUT_SEGUNDOS = 1


def abrir_puerto_serial():
    """
    Abre la comunicación serial con el ESP32-C6.

    Si el puerto está ocupado o no existe, se mostrará un error.
    """
    print("=== Lector JSON ESP32-C6 ===")
    print(f"[INFO] Intentando abrir puerto: {PUERTO_SERIAL}")
    print(f"[INFO] Baudrate: {BAUDRATE}")

    puerto = serial.Serial(
        port=PUERTO_SERIAL,
        baudrate=BAUDRATE,
        timeout=TIMEOUT_SEGUNDOS
    )

    # Pequeña espera para estabilizar la conexión serial
    time.sleep(2)

    print("[OK] Puerto serial abierto correctamente.")
    print("[INFO] Esperando mensajes del ESP32-C6...\n")

    return puerto


def procesar_linea(linea_texto):
    """
    Procesa una línea recibida desde el ESP32-C6.

    El ESP32-C6 puede enviar dos tipos de mensajes:
    1. Logs internos de ESP-IDF, por ejemplo:
       I (1234) PORTERIA_ESP32C6: Contador: 1 | RGB: VERDE

    2. Mensajes JSON, por ejemplo:
       {"origen":"ESP32C6","evento":"PING","contador":1,"rgb":"VERDE"}

    En este paso solo nos interesan las líneas JSON.
    """

    # Limpiar espacios, saltos de línea y caracteres invisibles
    linea_texto = linea_texto.strip()

    # Si la línea está vacía, no hacemos nada
    if not linea_texto:
        return

    # Solo intentamos procesar líneas que parezcan JSON
    if not linea_texto.startswith("{"):
        print(f"[LOG ESP32] {linea_texto}")
        return

    try:
        datos = json.loads(linea_texto)

        origen = datos.get("origen", "DESCONOCIDO")
        evento = datos.get("evento", "SIN_EVENTO")
        contador = datos.get("contador", "N/A")
        rgb = datos.get("rgb", "N/A")

        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(
            f"[JSON RECIBIDO] {fecha_hora} | "
            f"origen={origen} | "
            f"evento={evento} | "
            f"contador={contador} | "
            f"rgb={rgb}"
        )

    except json.JSONDecodeError:
        print(f"[ADVERTENCIA] Línea con formato JSON inválido: {linea_texto}")


def main():
    """
    Función principal del programa.

    Mantiene la lectura continua del puerto serial hasta que el usuario
    detenga el programa con Ctrl + C.
    """
    puerto = None

    try:
        puerto = abrir_puerto_serial()

        while True:
            # Leer una línea enviada por el ESP32-C6
            linea = puerto.readline()

            # Convertir bytes a texto.
            # errors='replace' evita que el programa se caiga si llega un carácter extraño.
            linea_texto = linea.decode("utf-8", errors="replace")

            procesar_linea(linea_texto)

    except serial.SerialException as error:
        print("[ERROR] No se pudo abrir o leer el puerto serial.")
        print(f"[DETALLE] {error}")
        print("\nPosibles causas:")
        print("- El ESP32-C6 no está conectado.")
        print("- El puerto /dev/ttyACM0 cambió.")
        print("- El monitor de ESP-IDF sigue abierto.")
        print("- Otro proceso está usando el puerto serial.")

    except KeyboardInterrupt:
        print("\n[INFO] Programa detenido por el usuario.")

    finally:
        if puerto is not None and puerto.is_open:
            puerto.close()
            print("[OK] Puerto serial cerrado correctamente.")


if __name__ == "__main__":
    main()