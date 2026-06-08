"""
Limpieza y seleccion de texto de placas.

El OCR puede devolver textos con espacios, guiones, puntos o caracteres raros.
Este modulo intenta convertir esas salidas en una placa limpia para comparar contra SQLite.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, Optional


_ALLOWED_PLATE_CHARS = re.compile(r"[^A-Z0-9]")

# Correcciones conservadoras para caracteres muy comunes en OCR de placas.
# Se aplican solo de forma general; si en el futuro se conoce el formato exacto,
# se puede hacer una correccion por posicion.
_COMMON_REPLACEMENTS = {
    "Á": "A",
    "É": "E",
    "Í": "I",
    "Ó": "O",
    "Ú": "U",
    "Ñ": "N",
}


@dataclass(frozen=True)
class OCRCandidate:
    """Candidato devuelto por el OCR."""

    text: str
    confidence: float = 0.0


def _remove_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def limpiar_texto_placa(texto: str, min_length: int = 5, max_length: int = 8) -> Optional[str]:
    """
    Limpia un texto OCR y devuelve una posible placa.

    Ejemplos:
        " A B C-123 " -> "ABC123"
        "abc 123"     -> "ABC123"
        "ABC.12D"     -> "ABC12D"

    Retorna None si el texto queda demasiado corto/largo.
    """

    if not texto:
        return None

    cleaned = texto.strip().upper()
    cleaned = _remove_accents(cleaned)

    for old, new in _COMMON_REPLACEMENTS.items():
        cleaned = cleaned.replace(old, new)

    cleaned = _ALLOWED_PLATE_CHARS.sub("", cleaned)

    if min_length <= len(cleaned) <= max_length:
        return cleaned

    return None


def seleccionar_mejor_placa(
    candidates: Iterable[OCRCandidate],
    min_length: int = 5,
    max_length: int = 8,
) -> Optional[OCRCandidate]:
    """
    Escoge el mejor candidato OCR luego de limpiar el texto.

    Criterio:
    1. Debe quedar dentro de la longitud permitida.
    2. Se prioriza mayor confianza.
    3. En empate, se prioriza longitud cercana a 6, comun en placas tipo ABC123.
    """

    valid_candidates: list[OCRCandidate] = []

    for candidate in candidates:
        plate = limpiar_texto_placa(candidate.text, min_length, max_length)
        if plate is not None:
            valid_candidates.append(OCRCandidate(text=plate, confidence=float(candidate.confidence)))

    if not valid_candidates:
        return None

    return sorted(
        valid_candidates,
        key=lambda item: (item.confidence, -abs(len(item.text) - 6)),
        reverse=True,
    )[0]
