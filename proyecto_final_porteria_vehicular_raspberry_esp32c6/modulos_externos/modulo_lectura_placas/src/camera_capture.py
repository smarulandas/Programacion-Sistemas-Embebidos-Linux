"""
Utilidad opcional para capturar una imagen desde una camara USB.

No se usa automaticamente porque la integracion real depende de la Raspberry/camara.
"""

from __future__ import annotations

from pathlib import Path

import cv2


def capturar_imagen_usb(output_path: str | Path, camera_index: int = 0) -> bool:
    """Captura una imagen desde una camara USB y la guarda en output_path."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        return False

    ok, frame = camera.read()
    camera.release()

    if not ok or frame is None:
        return False

    return bool(cv2.imwrite(str(output_path), frame))
