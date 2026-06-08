"""Modulo de lectura automatica de placas vehiculares."""

from .plate_reader import leer_placa_desde_imagen
from .config import PlateReaderConfig

__all__ = ["leer_placa_desde_imagen", "PlateReaderConfig"]
