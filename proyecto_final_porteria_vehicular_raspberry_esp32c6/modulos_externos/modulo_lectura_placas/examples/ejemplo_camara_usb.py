"""
Ejemplo opcional para capturar desde una camara USB y leer la placa.

Este ejemplo es para tu compañero, cuando ya tenga la Raspberry y la camara.
No requiere ESP32 para probarlo.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.camera_capture import capturar_imagen_usb  # noqa: E402
from src.plate_reader import leer_placa_desde_imagen  # noqa: E402


def main() -> None:
    ruta_captura = ROOT_DIR / "imagenes_prueba" / "captura_usb.jpg"

    ok = capturar_imagen_usb(ruta_captura, camera_index=0)
    if not ok:
        print("No se pudo capturar imagen desde la camara USB.")
        print("Revisar que la camara este conectada y que el indice sea correcto.")
        return

    resultado = leer_placa_desde_imagen(ruta_captura)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
