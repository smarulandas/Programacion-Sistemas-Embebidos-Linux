from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from src.plate_reader import leer_placa_desde_imagen


"""
Prueba de reconocimiento de placas con varias imágenes.

Este script evalúa el módulo completo:
- Detección YOLO.
- Recorte de placa.
- Lectura OCR.
- Limpieza del texto detectado.

Usa imágenes tomadas con la cámara Logitech 720p y guardadas en:
~/proyecto_porteria/imagenes/pruebas_camara/
"""


def probar_imagen(ruta_imagen):
    print("=" * 80)
    print(f"Imagen: {ruta_imagen}")

    if not ruta_imagen.exists():
        print("[ERROR] La imagen no existe.")
        return

    resultado = leer_placa_desde_imagen(str(ruta_imagen))

    estado = resultado.get("estado")
    placa = resultado.get("placa")
    confianza_deteccion = resultado.get("confianza_deteccion")
    confianza_ocr = resultado.get("confianza_ocr")
    mensaje = resultado.get("mensaje")

    print(f"Estado: {estado}")
    print(f"Placa detectada: {placa}")
    print(f"Confianza detección YOLO: {confianza_deteccion}")
    print(f"Confianza OCR: {confianza_ocr}")
    print(f"Mensaje: {mensaje}")

    if estado == "OK":
        print("[OK] Lectura automática exitosa.")
    elif estado == "SIN_PLACA":
        print("[ALERTA] YOLO no detectó placa.")
    elif estado == "OCR_FALLIDO":
        print("[ALERTA] Se detectó placa, pero OCR no leyó texto válido.")
    else:
        print("[ALERTA] Falló la lectura automática.")


def main():
    carpeta_imagenes = Path("/home/diseno_digital/proyecto_porteria/imagenes/pruebas_camara")

    imagenes = [
        carpeta_imagenes / "placa_prueba_1.jpg",
        carpeta_imagenes / "placa_prueba_2.jpg",
        carpeta_imagenes / "placa_prueba_3.jpg",
    ]

    print("=== Prueba múltiple de reconocimiento de placas ===")

    total = 0
    exitosas = 0

    for ruta_imagen in imagenes:
        total += 1
        probar_imagen(ruta_imagen)

        resultado = leer_placa_desde_imagen(str(ruta_imagen))
        if resultado.get("estado") == "OK":
            exitosas += 1

    print("=" * 80)
    print("=== Resumen final ===")
    print(f"Imágenes evaluadas: {total}")
    print(f"Lecturas exitosas: {exitosas}")
    print(f"Lecturas fallidas: {total - exitosas}")

    if exitosas == total:
        print("[RESULTADO] Todas las imágenes fueron leídas correctamente.")
    elif exitosas > 0:
        print("[RESULTADO] El modelo funciona, pero no es perfecto. Conviene mantener ingreso manual como respaldo.")
    else:
        print("[RESULTADO] El modelo no logró leer estas imágenes. Hay que mejorar captura o ajustar OCR.")


if __name__ == "__main__":
    main()