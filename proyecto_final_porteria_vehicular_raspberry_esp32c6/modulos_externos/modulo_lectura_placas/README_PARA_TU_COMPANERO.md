# Módulo de lectura automática de placas

Este ZIP contiene un módulo independiente para detectar y leer placas vehiculares desde imágenes.

Está pensado para integrarse después al proyecto de portería vehicular con Raspberry Pi 400 y ESP32-C6, pero **no modifica directamente el proyecto principal**.

---

## 1. ¿Qué hace este módulo?

Flujo general:

```text
Imagen de un vehículo
        ↓
YOLO detecta la zona donde está la placa
        ↓
Se recorta la placa
        ↓
EasyOCR intenta leer letras y números
        ↓
Se limpia el texto
        ↓
Se devuelve una placa lista para comparar en SQLite
```

La función principal devuelve algo como:

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

---

## 2. ¿Qué NO hace todavía?

Este módulo **no controla el ESP32-C6**, **no abre la puerta**, **no modifica SQLite** y **no cambia el `main.py` del parqueadero**.

Solo entrega la placa leída para que el proyecto principal la compare.

---

## 3. Requisitos

Instalar dependencias desde la carpeta de este módulo:

```bash
pip install -r requirements_vision.txt
```

Dependencias principales:

```text
ultralytics
opencv-python
easyocr
numpy
```

En Raspberry Pi puede tardar porque `easyocr` y `torch` son pesados.

---

## 4. Prueba básica sin cámara

Esta prueba no necesita ESP32 ni cámara:

```bash
python tests/test_sin_camara.py
```

Debe revisar si existe el modelo y si están instaladas las dependencias.

También se puede probar la limpieza de texto:

```bash
python tests/test_limpiar_texto.py
```

---

## 5. Prueba con una imagen guardada

Poner una foto en:

```text
imagenes_prueba/foto_carro.jpg
```

Luego ejecutar:

```bash
python tests/test_desde_imagen.py imagenes_prueba/foto_carro.jpg
```

O también:

```bash
python examples/ejemplo_uso_simple.py imagenes_prueba/foto_carro.jpg
```

---

## 6. Uso desde otro archivo Python

La función principal es:

```python
from src.plate_reader import leer_placa_desde_imagen

resultado = leer_placa_desde_imagen("imagenes_prueba/foto_carro.jpg")

if resultado["estado"] == "OK":
    placa = resultado["placa"]
    print("Placa lista para comparar:", placa)
else:
    print("No se pudo leer placa:", resultado["mensaje"])
```

---

## 7. Estados posibles

| Estado | Significado |
|---|---|
| `OK` | Se detectó placa y el OCR leyó texto válido. |
| `SIN_PLACA` | YOLO no detectó ninguna placa en la imagen. |
| `OCR_FALLIDO` | Se detectó una placa, pero el OCR no leyó bien el texto. |
| `ERROR` | Falló la lectura de imagen, dependencia, modelo o procesamiento. |

---

## 8. Integración recomendada con el parqueadero

En el proyecto actual, la placa se pide manualmente. La idea es reemplazar la línea donde se hace algo como:

```python
placa = input("Digite la placa: ")
```

por una lógica con respaldo manual:

```python
from src.plate_reader import leer_placa_desde_imagen

resultado = leer_placa_desde_imagen("imagenes_prueba/captura_actual.jpg")

if resultado["estado"] == "OK":
    placa = resultado["placa"]
else:
    print(resultado["mensaje"])
    placa = input("No se pudo leer automaticamente. Digite la placa manualmente: ")
```

Así, si la cámara o el OCR fallan, el sistema sigue funcionando.

---

## 9. Cámara USB

Se incluye un ejemplo opcional:

```bash
python examples/ejemplo_camara_usb.py
```

Este ejemplo intenta capturar una imagen con una cámara USB usando OpenCV.

Si no funciona, revisar:

```text
- que la cámara esté conectada
- que la Raspberry la reconozca
- que el índice de cámara sea 0 o cambiarlo a 1
```

---

## 10. Modelo incluido

El modelo está en:

```text
modelo/best_plate_yolo11m.pt
```

Ese modelo detecta la región de la placa. Para leer el número se usa OCR.

---

## 11. Recomendación importante

Primero probar con imágenes guardadas. Después conectar cámara. Finalmente integrar con el flujo de entrada/salida del ESP32-C6.

Orden recomendado:

```text
1. Instalar dependencias.
2. Ejecutar test_sin_camara.py.
3. Probar una foto guardada.
4. Probar cámara USB.
5. Integrar con main.py del parqueadero.
6. Mantener respaldo manual si el OCR falla.
```
