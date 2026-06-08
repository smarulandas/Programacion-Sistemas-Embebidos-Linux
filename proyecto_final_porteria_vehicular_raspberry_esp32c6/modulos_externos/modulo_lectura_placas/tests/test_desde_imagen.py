"""
Prueba desde una imagen guardada.

Ejecutar:
    python tests/test_desde_imagen.py imagenes_prueba/foto_carro.jpg
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.plate_reader import leer_placa_desde_imagen  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python tests/test_desde_imagen.py RUTA_IMAGEN")
        return

    resultado = leer_placa_desde_imagen(sys.argv[1])
    print(json.dumps(resultado, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
