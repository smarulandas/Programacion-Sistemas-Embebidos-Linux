"""
Configuracion central del modulo de lectura de placas.

Este archivo NO depende de Raspberry ni ESP32. Solo define rutas y umbrales.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "modelo" / "best_plate_yolo11m.pt"


@dataclass(frozen=True)
class PlateReaderConfig:
    """Parametros principales del lector de placas."""

    model_path: Path = MODEL_PATH

    # Umbral minimo de confianza para aceptar una deteccion YOLO.
    detection_confidence: float = 0.35

    # Tamanio de imagen usado por YOLO. 640 coincide con el entrenamiento del modelo.
    image_size: int = 640

    # Margen extra alrededor de la caja detectada antes de recortar la placa.
    crop_padding_ratio: float = 0.08

    # Idiomas de EasyOCR. Para placas latinas, ingles suele funcionar bien con letras/numeros.
    ocr_languages: Tuple[str, ...] = ("en",)

    # Umbral minimo de confianza promedio del OCR para aceptar el texto.
    ocr_confidence: float = 0.25

    # Longitud aceptada luego de limpiar el texto.
    min_plate_length: int = 5
    max_plate_length: int = 8

    # Si True, guarda recortes/imagenes depuradas en carpeta debug.
    save_debug_images: bool = False

    # Carpeta donde se guardan salidas de depuracion cuando save_debug_images=True.
    debug_dir: Path = BASE_DIR / "debug"
