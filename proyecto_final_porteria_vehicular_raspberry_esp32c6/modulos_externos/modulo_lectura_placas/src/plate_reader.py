"""
Funcion principal del modulo.

Tu compañero deberia importar principalmente:

    from src.plate_reader import leer_placa_desde_imagen

Y usar:

    resultado = leer_placa_desde_imagen("foto.jpg")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import cv2

from .config import PlateReaderConfig
from .plate_detector import PlateDetector
from .plate_ocr import PlateOCR


def _response(
    estado: str,
    placa: Optional[str],
    mensaje: str,
    confianza_deteccion: float = 0.0,
    confianza_ocr: float = 0.0,
    bbox: Optional[tuple[int, int, int, int]] = None,
    raw_ocr: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    return {
        "estado": estado,
        "placa": placa,
        "confianza_deteccion": round(float(confianza_deteccion), 4),
        "confianza_ocr": round(float(confianza_ocr), 4),
        "bbox": list(bbox) if bbox is not None else None,
        "mensaje": mensaje,
        "raw_ocr": raw_ocr or [],
    }


def leer_placa_desde_imagen(
    ruta_imagen: str | Path,
    config: Optional[PlateReaderConfig] = None,
) -> dict[str, Any]:
    """
    Detecta y lee una placa desde una imagen.

    Retorna siempre un diccionario con este formato:
        {
            "estado": "OK" | "SIN_PLACA" | "OCR_FALLIDO" | "ERROR",
            "placa": "ABC123" o None,
            "confianza_deteccion": float,
            "confianza_ocr": float,
            "bbox": [x1, y1, x2, y2] o None,
            "mensaje": str,
            "raw_ocr": lista de candidatos OCR
        }
    """

    config = config or PlateReaderConfig()
    image_path = Path(ruta_imagen)

    try:
        if not image_path.exists():
            return _response(
                estado="ERROR",
                placa=None,
                mensaje=f"No existe la imagen: {image_path}",
            )

        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            return _response(
                estado="ERROR",
                placa=None,
                mensaje=f"OpenCV no pudo leer la imagen: {image_path}",
            )

        detector = PlateDetector(config)
        detection = detector.detect_best(image_bgr)

        if detection is None:
            return _response(
                estado="SIN_PLACA",
                placa=None,
                mensaje="No se detecto ninguna placa en la imagen.",
            )

        if config.save_debug_images:
            config.debug_dir.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(config.debug_dir / "ultimo_recorte_placa.jpg"), detection.crop)

        ocr = PlateOCR(config)
        ocr_result = ocr.read_text(detection.crop)

        raw_ocr = [
            {"texto": candidate.text, "confianza": round(float(candidate.confidence), 4)}
            for candidate in ocr_result.raw_candidates
        ]

        if ocr_result.text is None or ocr_result.confidence < config.ocr_confidence:
            return _response(
                estado="OCR_FALLIDO",
                placa=None,
                confianza_deteccion=detection.confidence,
                confianza_ocr=ocr_result.confidence,
                bbox=detection.bbox,
                mensaje="Se detecto una placa, pero el OCR no pudo leerla con suficiente confianza.",
                raw_ocr=raw_ocr,
            )

        return _response(
            estado="OK",
            placa=ocr_result.text,
            confianza_deteccion=detection.confidence,
            confianza_ocr=ocr_result.confidence,
            bbox=detection.bbox,
            mensaje="Placa detectada y leida correctamente.",
            raw_ocr=raw_ocr,
        )

    except Exception as exc:  # noqa: BLE001 - Se devuelve como respuesta controlada para no tumbar el sistema principal.
        return _response(
            estado="ERROR",
            placa=None,
            mensaje=f"Error procesando imagen: {exc}",
        )
