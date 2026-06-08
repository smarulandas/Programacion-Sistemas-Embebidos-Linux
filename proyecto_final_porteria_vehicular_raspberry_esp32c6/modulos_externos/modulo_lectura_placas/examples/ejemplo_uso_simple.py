"""
Ejemplo minimo de uso del modulo.

Ejecutar desde la carpeta modulo_lectura_placas:

    python examples/ejemplo_uso_simple.py imagenes_prueba/foto_carro.jpg
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Permite importar src cuando se ejecuta este archivo desde examples/.
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.plate_reader import leer_placa_desde_imagen  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python examples/ejemplo_uso_simple.py RUTA_IMAGEN")
        return

    ruta_imagen = sys.argv[1]
    resultado = leer_placa_desde_imagen(ruta_imagen)

    print(json.dumps(resultado, indent=4, ensure_ascii=False))

    if resultado["estado"] == "OK":
        print(f"\nPlaca final para comparar en SQLite: {resultado['placa']}")
    else:
        print("\nNo se obtuvo placa automaticamente. Se recomienda pedir ingreso manual.")


if __name__ == "__main__":
    main()
