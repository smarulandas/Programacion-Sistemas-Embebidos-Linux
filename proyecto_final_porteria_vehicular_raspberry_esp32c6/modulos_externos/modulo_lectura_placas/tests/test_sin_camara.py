"""
Prueba de instalacion basica.

No necesita camara ni ESP32. Verifica:
- existencia del modelo
- importacion de OpenCV
- importacion opcional de ultralytics/easyocr
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.config import MODEL_PATH  # noqa: E402


def check_module(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def main() -> None:
    print("Verificando modulo de lectura de placas...")
    print(f"Modelo esperado: {MODEL_PATH}")

    if MODEL_PATH.exists():
        print(f"OK: modelo encontrado ({MODEL_PATH.stat().st_size / (1024 * 1024):.1f} MB)")
    else:
        print("ERROR: no se encontro el modelo YOLO.")

    for module_name in ["cv2", "ultralytics", "easyocr", "numpy"]:
        if check_module(module_name):
            print(f"OK: {module_name} instalado")
        else:
            print(f"FALTA: {module_name}")

    print("\nSi falta alguna dependencia, ejecutar:")
    print("pip install -r requirements_vision.txt")


if __name__ == "__main__":
    main()
