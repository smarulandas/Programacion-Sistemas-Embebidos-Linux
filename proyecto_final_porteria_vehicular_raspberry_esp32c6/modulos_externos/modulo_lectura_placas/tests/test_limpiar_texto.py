"""
Prueba basica que no necesita modelo YOLO ni EasyOCR.
Sirve para verificar que Python puede importar el modulo.
"""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.plate_text_cleaner import limpiar_texto_placa  # noqa: E402


def main() -> None:
    casos = {
        " A B C-123 ": "ABC123",
        "abc 123": "ABC123",
        "ABC.12D": "ABC12D",
        "@@@": None,
    }

    for entrada, esperado in casos.items():
        obtenido = limpiar_texto_placa(entrada)
        print(f"Entrada: {entrada!r} -> Obtenido: {obtenido!r}")
        assert obtenido == esperado, f"Fallo: {entrada!r}. Esperado {esperado!r}, obtenido {obtenido!r}"

    print("OK: limpieza de texto funcionando.")


if __name__ == "__main__":
    main()
