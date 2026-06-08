# Notas de integración con el proyecto de portería vehicular

Este documento es para quien vaya a integrar el módulo al proyecto principal.

---

## Objetivo

Reemplazar el ingreso manual de la placa por lectura automática desde imagen, sin romper la lógica actual de la base de datos.

El sistema actual hace aproximadamente esto:

```text
ESP32-C6 envía evento ENTRADA/SALIDA
        ↓
Raspberry recibe evento
        ↓
Raspberry pide placa manualmente
        ↓
Raspberry compara placa con SQLite
        ↓
Raspberry responde AUTORIZADO o NO_AUTORIZADO
```

Con este módulo, la parte a reemplazar es solamente:

```text
Raspberry pide placa manualmente
```

por:

```text
Raspberry captura imagen
        ↓
Módulo lee placa
        ↓
Si falla, pedir placa manualmente
```

---

## Función principal a usar

```python
from src.plate_reader import leer_placa_desde_imagen

resultado = leer_placa_desde_imagen("ruta/de/la/imagen.jpg")
```

---

## Respuesta esperada

```python
{
    "estado": "OK",
    "placa": "ABC123",
    "confianza_deteccion": 0.91,
    "confianza_ocr": 0.84,
    "bbox": [120, 80, 340, 160],
    "mensaje": "Placa detectada y leida correctamente.",
    "raw_ocr": []
}
```

Para el proyecto principal solo se necesita:

```python
placa = resultado["placa"]
```

cuando:

```python
resultado["estado"] == "OK"
```

---

## Integración mínima sugerida

```python
from src.plate_reader import leer_placa_desde_imagen


def obtener_placa_con_respaldo_manual(ruta_imagen):
    resultado = leer_placa_desde_imagen(ruta_imagen)

    if resultado["estado"] == "OK":
        return resultado["placa"]

    print("No se pudo leer la placa automáticamente.")
    print("Motivo:", resultado["mensaje"])

    return input("Digite la placa manualmente: ").strip().upper()
```

---

## Dónde integrarlo en el proyecto original

Buscar en el `main.py` del proyecto de portería la parte donde se pide la placa con `input()`.

La idea es cambiar esa parte por:

```python
placa = obtener_placa_con_respaldo_manual("imagenes/captura_actual.jpg")
```

No se recomienda eliminar el respaldo manual.

---

## Captura de imagen

Este módulo incluye:

```python
from src.camera_capture import capturar_imagen_usb
```

Ejemplo:

```python
capturar_imagen_usb("imagenes/captura_actual.jpg", camera_index=0)
```

Pero la captura real puede variar según la cámara y la Raspberry.

---

## Riesgos conocidos

1. **YOLO detecta la placa, pero OCR puede fallar.**
   Por eso se mantiene entrada manual de respaldo.

2. **EasyOCR puede ser pesado para Raspberry Pi.**
   Si va lento, probar primero con imágenes pequeñas o considerar Tesseract como alternativa.

3. **La calidad de la cámara afecta mucho.**
   Debe haber buena luz, placa enfocada y poco movimiento.

4. **El modelo no lee texto directamente.**
   El modelo detecta placa; el texto lo lee EasyOCR.

---

## Flujo recomendado final

```text
Evento ENTRADA/SALIDA desde ESP32
        ↓
Raspberry captura imagen
        ↓
leer_placa_desde_imagen()
        ↓
Si estado == OK → usar placa leída
        ↓
Si no → pedir placa manual
        ↓
Comparar placa en SQLite
        ↓
Responder al ESP32
```
