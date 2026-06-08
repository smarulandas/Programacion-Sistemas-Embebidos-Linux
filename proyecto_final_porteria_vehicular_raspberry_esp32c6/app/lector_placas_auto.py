from pathlib import Path
import sys


"""
Proyecto: Sistema de portería vehicular

Paso 24:
Puente entre la aplicación principal de portería y el módulo externo
de lectura automática de placas.

Este archivo permite usar el módulo:

modulos_externos/modulo_lectura_placas

desde app/main.py sin mezclar directamente el código externo
con la lógica principal del sistema.
"""


BASE_DIR = Path(__file__).resolve().parents[1]

MODULO_PLACAS_DIR = BASE_DIR / "modulos_externos" / "modulo_lectura_placas"

if str(MODULO_PLACAS_DIR) not in sys.path:
    sys.path.insert(0, str(MODULO_PLACAS_DIR))


try:
    from src.plate_reader import leer_placa_desde_imagen
except Exception as error:
    leer_placa_desde_imagen = None
    ERROR_IMPORTACION = str(error)
else:
    ERROR_IMPORTACION = None


def resolver_ruta_imagen(ruta_imagen):
    """
    Convierte una ruta relativa o absoluta en una ruta absoluta válida.

    Ejemplo:
    imagenes/eventos/evento_ENTRADA_PENDIENTE.jpg
    ->
    /home/diseno_digital/proyecto_porteria/imagenes/eventos/evento_ENTRADA_PENDIENTE.jpg
    """

    ruta = Path(ruta_imagen)

    if ruta.is_absolute():
        return ruta

    return BASE_DIR / ruta


def detectar_placa_automatica(ruta_imagen):
    """
    Intenta detectar y leer automáticamente la placa desde una imagen.

    Retorna un diccionario con:

    {
        "ok": True/False,
        "placa": "ABC123" o None,
        "estado": "OK", "SIN_PLACA", "OCR_FALLIDO", "ERROR",
        "confianza_deteccion": valor numérico,
        "confianza_ocr": valor numérico,
        "mensaje": texto explicativo
    }
    """

    print("[LECTOR PLACAS] Intentando lectura automática...")

    if leer_placa_desde_imagen is None:
        print("[LECTOR PLACAS] No se pudo importar el módulo de placas.")
        print(f"[LECTOR PLACAS] Detalle: {ERROR_IMPORTACION}")

        return {
            "ok": False,
            "placa": None,
            "estado": "ERROR",
            "confianza_deteccion": 0.0,
            "confianza_ocr": 0.0,
            "mensaje": "No se pudo importar el módulo de lectura de placas."
        }

    ruta_absoluta = resolver_ruta_imagen(ruta_imagen)

    if not ruta_absoluta.exists():
        print(f"[LECTOR PLACAS] La imagen no existe: {ruta_absoluta}")

        return {
            "ok": False,
            "placa": None,
            "estado": "ERROR",
            "confianza_deteccion": 0.0,
            "confianza_ocr": 0.0,
            "mensaje": "La imagen no existe."
        }

    try:
        resultado = leer_placa_desde_imagen(str(ruta_absoluta))

        estado = resultado.get("estado")
        placa = resultado.get("placa")
        confianza_deteccion = resultado.get("confianza_deteccion", 0.0)
        confianza_ocr = resultado.get("confianza_ocr", 0.0)
        mensaje = resultado.get("mensaje", "")

        print(f"[LECTOR PLACAS] Estado: {estado}")
        print(f"[LECTOR PLACAS] Placa detectada: {placa}")
        print(f"[LECTOR PLACAS] Confianza detección: {confianza_deteccion}")
        print(f"[LECTOR PLACAS] Confianza OCR: {confianza_ocr}")

        if estado == "OK" and placa:
            return {
                "ok": True,
                "placa": placa,
                "estado": estado,
                "confianza_deteccion": confianza_deteccion,
                "confianza_ocr": confianza_ocr,
                "mensaje": mensaje
            }

        return {
            "ok": False,
            "placa": None,
            "estado": estado,
            "confianza_deteccion": confianza_deteccion,
            "confianza_ocr": confianza_ocr,
            "mensaje": mensaje
        }

    except Exception as error:
        print("[LECTOR PLACAS] Error durante la lectura automática.")
        print(f"[LECTOR PLACAS] Detalle: {error}")

        return {
            "ok": False,
            "placa": None,
            "estado": "ERROR",
            "confianza_deteccion": 0.0,
            "confianza_ocr": 0.0,
            "mensaje": str(error)
        }