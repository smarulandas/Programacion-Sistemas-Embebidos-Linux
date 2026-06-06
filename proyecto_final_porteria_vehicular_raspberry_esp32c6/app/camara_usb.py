from pathlib import Path
from datetime import datetime
import subprocess


"""
Proyecto: Sistema embebido de portería vehicular

Paso 21:
Módulo de cámara USB.

Este archivo se encarga de:
- Crear nombres ordenados para imágenes.
- Capturar una foto usando fswebcam.
- Guardar la imagen en la carpeta imagenes/eventos/.
- Retornar la ruta de la imagen para guardarla en SQLite.

La cámara usada es una Logitech 720p detectada como:
/dev/video0
"""


# =========================
# Configuración de cámara
# =========================

DISPOSITIVO_CAMARA = "/dev/video0"
RESOLUCION_CAMARA = "1280x720"
FRAMES_DESCARTADOS = "20"
RETARDO_SEGUNDOS = "2"


# =========================
# Rutas del proyecto
# =========================

BASE_DIR = Path(__file__).resolve().parents[1]
IMAGENES_DIR = BASE_DIR / "imagenes"
EVENTOS_IMG_DIR = IMAGENES_DIR / "eventos"


def limpiar_texto_archivo(texto):
    """
    Limpia un texto para usarlo dentro del nombre de un archivo.

    Ejemplo:
    "ABC 123" -> "ABC123"
    "ALERTA/SALIDA" -> "ALERTA_SALIDA"
    """

    texto_limpio = texto.strip().upper()
    texto_limpio = texto_limpio.replace(" ", "")
    texto_limpio = texto_limpio.replace("-", "")
    texto_limpio = texto_limpio.replace("/", "_")
    texto_limpio = texto_limpio.replace(":", "_")

    return texto_limpio


def crear_nombre_imagen(evento, placa):
    """
    Crea un nombre único para la imagen del evento.

    Formato:
    evento_ENTRADA_ABC123_2026_06_05_193000.jpg
    """

    fecha_hora = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    evento_limpio = limpiar_texto_archivo(evento)
    placa_limpia = limpiar_texto_archivo(placa)

    nombre_archivo = f"evento_{evento_limpio}_{placa_limpia}_{fecha_hora}.jpg"

    return nombre_archivo


def capturar_imagen_evento(evento, placa):
    """
    Captura una imagen usando fswebcam.

    Retorna:
    - Ruta relativa de la imagen si la captura fue exitosa.
    - "SIN_CAMARA" si ocurre algún error.

    La ruta relativa es la que se guarda en SQLite.
    """

    try:
        EVENTOS_IMG_DIR.mkdir(parents=True, exist_ok=True)

        nombre_imagen = crear_nombre_imagen(evento, placa)
        ruta_imagen = EVENTOS_IMG_DIR / nombre_imagen

        comando = [
            "fswebcam",
            "-d", DISPOSITIVO_CAMARA,
            "-r", RESOLUCION_CAMARA,
            "--skip", FRAMES_DESCARTADOS,
            "--delay", RETARDO_SEGUNDOS,
            "--no-banner",
            str(ruta_imagen)
        ]

        print("[CAMARA] Capturando imagen del evento...")
        print(f"[CAMARA] Evento: {evento} | Placa: {placa}")
        print(f"[CAMARA] Ruta destino: {ruta_imagen}")

        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=10
        )

        if resultado.returncode != 0:
            print("[CAMARA] Error al capturar imagen.")
            print(f"[CAMARA] Detalle: {resultado.stderr.strip()}")
            return "SIN_CAMARA"

        if not ruta_imagen.exists():
            print("[CAMARA] No se encontró la imagen después de capturar.")
            return "SIN_CAMARA"

        if ruta_imagen.stat().st_size == 0:
            print("[CAMARA] La imagen fue creada pero está vacía.")
            return "SIN_CAMARA"

        ruta_relativa = ruta_imagen.relative_to(BASE_DIR)

        print(f"[CAMARA] Imagen guardada correctamente: {ruta_relativa}")

        return str(ruta_relativa)

    except subprocess.TimeoutExpired:
        print("[CAMARA] Tiempo agotado esperando respuesta de la cámara.")
        return "SIN_CAMARA"

    except Exception as error:
        print("[CAMARA] Error inesperado capturando imagen.")
        print(f"[CAMARA] Detalle: {error}")
        return "SIN_CAMARA"