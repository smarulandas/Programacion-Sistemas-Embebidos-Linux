"""
Deteccion de placas con YOLO.

Este modulo carga el modelo best_plate_yolo11m.pt y devuelve recortes de placa.
No lee texto; solo detecta la zona donde esta la placa.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from .config import PlateReaderConfig


@dataclass(frozen=True)
class PlateDetection:
    """Resultado de una deteccion individual de placa."""

    bbox: tuple[int, int, int, int]
    confidence: float
    crop: np.ndarray


class PlateDetector:
    """Detector YOLO para placas vehiculares."""

    def __init__(self, config: Optional[PlateReaderConfig] = None):
        self.config = config or PlateReaderConfig()
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model

        if not Path(self.config.model_path).exists():
            raise FileNotFoundError(f"No se encontro el modelo YOLO: {self.config.model_path}")

        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ImportError(
                "No esta instalado ultralytics. Instala dependencias con: "
                "pip install -r requirements_vision.txt"
            ) from exc

        self._model = YOLO(str(self.config.model_path))
        return self._model

    @staticmethod
    def _add_padding(
        bbox: tuple[int, int, int, int],
        image_shape: tuple[int, int, int],
        padding_ratio: float,
    ) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = bbox
        height, width = image_shape[:2]

        box_width = max(x2 - x1, 1)
        box_height = max(y2 - y1, 1)
        pad_x = int(box_width * padding_ratio)
        pad_y = int(box_height * padding_ratio)

        return (
            max(0, x1 - pad_x),
            max(0, y1 - pad_y),
            min(width, x2 + pad_x),
            min(height, y2 + pad_y),
        )

    def detect_best(self, image_bgr: np.ndarray) -> Optional[PlateDetection]:
        """Detecta la placa con mayor confianza en una imagen BGR de OpenCV."""

        if image_bgr is None or image_bgr.size == 0:
            raise ValueError("La imagen esta vacia o no pudo leerse.")

        model = self._load_model()
        results = model.predict(
            source=image_bgr,
            imgsz=self.config.image_size,
            conf=self.config.detection_confidence,
            verbose=False,
        )

        if not results:
            return None

        boxes = getattr(results[0], "boxes", None)
        if boxes is None or len(boxes) == 0:
            return None

        detections: list[PlateDetection] = []

        for box in boxes:
            confidence = float(box.conf[0])
            if confidence < self.config.detection_confidence:
                continue

            x1, y1, x2, y2 = [int(value) for value in box.xyxy[0].tolist()]
            padded_bbox = self._add_padding(
                (x1, y1, x2, y2),
                image_bgr.shape,
                self.config.crop_padding_ratio,
            )
            px1, py1, px2, py2 = padded_bbox
            crop = image_bgr[py1:py2, px1:px2]

            if crop.size == 0:
                continue

            detections.append(
                PlateDetection(
                    bbox=padded_bbox,
                    confidence=confidence,
                    crop=crop,
                )
            )

        if not detections:
            return None

        return max(detections, key=lambda detection: detection.confidence)
