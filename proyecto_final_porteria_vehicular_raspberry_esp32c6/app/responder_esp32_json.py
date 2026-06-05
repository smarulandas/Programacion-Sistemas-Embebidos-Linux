import json
import time
from datetime import datetime

import serial


"""
Proyecto: Sistema embebido de portería vehicular

Paso 9:
Este programa corre en la Raspberry Pi 400.

Funciones:
- Lee mensajes JSON enviados por el ESP32-C6.
- Decodifica el evento recibido.
- Envía una respuesta al ESP32-C6.
- Muestra los logs que el ESP32-C6 devuelve.

Este paso verifica comunicación bidireccional:
ESP32-C6 -> Raspberry Pi
Raspberry Pi -> ESP32-C6
"""


PUERTO_SERIAL = "/dev/ttyACM0"
BAUDRATE = 115200
TIMEOUT_SEGUNDOS = 1


def abrir_puerto_serial():
    print("=== Responder JSON ESP32-C6 ===")
    print(f"[INFO] Abriendo puerto: {PUERTO_SERIAL}")
    print(f"[INFO] Baudrate: {BAUDRATE}")

    puerto = serial.Serial(
        port=PUERTO_SERIAL,
        baudrate=BAUDRATE,
        timeout=TIMEOUT_SEGUNDOS
    )

    # Espera corta para estabilizar la comunicación
    time.sleep(2)

    print("[OK] Puerto serial abierto.")
    print("[INFO] Esperando JSON del ESP32-C6...\n")

    return puerto


def enviar_respuesta(puerto, evento, contador):
    """
    Envía una respuesta simple al ESP32-C6.

    Por ahora, si llega evento PING, respondemos:
    ACK:PING:<contador>
    """
    respuesta = f"ACK:{evento}:{contador}\n"

    puerto.write(respuesta.encode("utf-8"))
    puerto.flush()

    print(f"[RESPUESTA ENVIADA] {respuesta.strip()}")


def procesar_linea(puerto, linea_texto):
    linea_texto = linea_texto.strip()

    if not linea_texto:
        return

    # Si no es JSON, lo mostramos como log del ESP32
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

        enviar_respuesta(puerto, evento, contador)

    except json.JSONDecodeError:
        print(f"[ADVERTENCIA] JSON inválido: {linea_texto}")


def main():
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

    except KeyboardInterrupt:
        print("\n[INFO] Programa detenido por el usuario.")

    finally:
        if puerto is not None and puerto.is_open:
            puerto.close()
            print("[OK] Puerto serial cerrado.")


if __name__ == "__main__":
    main()