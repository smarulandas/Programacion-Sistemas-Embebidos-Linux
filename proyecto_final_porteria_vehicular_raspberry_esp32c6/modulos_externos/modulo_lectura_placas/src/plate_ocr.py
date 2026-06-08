"""
OCR para leer el texto de una placa recortada.

Por defecto usa EasyOCR porque es facil de instalar en Python.
Si en Raspberry va lento, el proyecto puede seguir funcionando con entrada manual como respaldo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

from .config import PlateReaderConfig
from .plate_text_cleaner import OCRCandidate, seleccionar_mejor_placa


@dataclass(frozen=True)
class OCRResult:
    """Resultado del OCR."""

    text: Optional[str]
    confidence: float
    raw_candidates: list[OCRCandidate]


class PlateOCR:
    """Lector OCR para placas."""

    def __init__(self, config: Optional[PlateReaderConfig] = None):
        self.config = config or PlateReaderConfig()
        self._reader = None

    def _load_reader(self):
        if self._reader is not None:
            return self._reader

        try:
            import easyocr
        except ImportError as exc:
            raise ImportError(
                "No esta instalado easyocr. Instala dependencias con: "
                "pip install -r requirements_vision.txt"
            ) from exc

        # gpu=False para que funcione en Raspberry o PC sin GPU.
        self._reader = easyocr.Reader(list(self.config.ocr_languages), gpu=False)
        return self._reader

    @staticmethod
    def _preprocess_variants(image_bgr: np.ndarray) -> list[np.ndarray]:
        """
        Genera varias versiones de la placa para mejorar el OCR.
        Todas siguen siendo imagenes OpenCV/Numpy.
        """

        variants: list[np.ndarray] = []
        variants.append(image_bgr)

        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        variants.append(gray)

        # Aumentar tamanio ayuda mucho si la placa quedo pequena.
        scale = 2
        resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        variants.append(resized)

        blurred = cv2.GaussianBlur(resized, (3, 3), 0)
        _, thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(thresholded)

        return variants

    def read_text(self, plate_crop_bgr: np.ndarray) -> OCRResult:
        """Lee texto desde el recorte de una placa."""

        if plate_crop_bgr is None or plate_crop_bgr.size == 0:
            raise ValueError("El recorte de placa esta vacio.")

        reader = self._load_reader()
        raw_candidates: list[OCRCandidate] = []

        for variant in self._preprocess_variants(plate_crop_bgr):
            ocr_output = reader.readtext(variant, detail=1, paragraph=False)
            for item in ocr_output:
                # EasyOCR devuelve: (bbox, text, confidence)
                if len(item) >= 3:
                    raw_candidates.append(OCRCandidate(text=str(item[1]), confidence=float(item[2])))

        best = seleccionar_mejor_placa(
            raw_candidates,
            min_length=self.config.min_plate_length,
            max_length=self.config.max_plate_length,
        )

        if best is None:
            return OCRResult(text=None, confidence=0.0, raw_candidates=raw_candidates)

        return OCRResult(text=best.text, confidence=best.confidence, raw_candidates=raw_candidates)
