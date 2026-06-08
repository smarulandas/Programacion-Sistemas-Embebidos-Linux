"""
Ejemplo de integracion con el proyecto de porteria.

Este archivo NO modifica el proyecto principal. Solo muestra la idea para reemplazar
la entrada manual de placa por lectura automatica desde imagen.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.plate_reader import leer_placa_desde_imagen  # noqa: E402


def obtener_placa_para_porteria(ruta_imagen: str) -> str:
    """
    Intenta leer la placa con IA.
    Si falla, conserva respaldo manual para que el sistema no se caiga.
    """

    resultado = leer_placa_desde_imagen(ruta_imagen)

    if resultado["estado"] == "OK":
        placa = resultado["placa"]
        print(f"Placa leida automaticamente: {placa}")
        return placa

    print("No se pudo leer la placa automaticamente.")
    print(f"Motivo: {resultado['mensaje']}")

    # Respaldo manual recomendado para no bloquear el parqueadero.
    placa_manual = input("Digite la placa manualmente: ").strip().upper()
    return placa_manual


# Ejemplo conceptual: esta variable seria la imagen capturada por la camara.
ruta_captura = "imagenes_prueba/foto_carro.jpg"

# En el main.py del parqueadero, esta placa se usaria para consultar SQLite.
placa_detectada = obtener_placa_para_porteria(ruta_captura)
print(f"Placa lista para comparar en base de datos: {placa_detectada}")
