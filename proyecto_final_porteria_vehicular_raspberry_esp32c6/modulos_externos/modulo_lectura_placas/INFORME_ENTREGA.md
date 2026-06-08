# Informe de entrega del módulo

## Qué se entrega

Se entrega un módulo independiente para lectura automática de placas vehiculares desde imágenes.

Incluye:

- Modelo YOLO `best_plate_yolo11m.pt`.
- Código Python separado por responsabilidades.
- OCR con EasyOCR.
- Limpieza de texto de placa.
- Ejemplos de uso.
- Pruebas básicas.
- Notas de integración con el proyecto de portería vehicular.

---

## Validaciones realizadas antes de entregar

Se validó:

```text
- Estructura del módulo.
- Existencia del modelo en modelo/best_plate_yolo11m.pt.
- Compilación de archivos Python sin errores de sintaxis.
- Prueba de limpieza de texto de placa.
- Prueba básica sin cámara.
```

La prueba de limpieza funcionó correctamente con casos como:

```text
" A B C-123 " -> "ABC123"
"abc 123"     -> "ABC123"
"ABC.12D"     -> "ABC12D"
```

---

## Qué no se pudo validar aquí

No se pudo validar la detección real ni el OCR real porque este entorno no tiene instalados:

```text
ultralytics
easyocr
```

Tampoco se validó con Raspberry Pi, ESP32-C6 ni cámara física.

Por eso el módulo se entrega con respaldo manual recomendado para que el proyecto principal no se bloquee si la lectura automática falla.

---

## Primera prueba recomendada para el compañero

Desde la carpeta del módulo:

```bash
pip install -r requirements_vision.txt
python tests/test_sin_camara.py
python tests/test_limpiar_texto.py
python tests/test_desde_imagen.py imagenes_prueba/foto_carro.jpg
```

Antes de la última prueba, debe copiar una foto real en:

```text
imagenes_prueba/foto_carro.jpg
```

---

## Punto de integración principal

La función que debe usar el proyecto de portería es:

```python
from src.plate_reader import leer_placa_desde_imagen
```

Uso:

```python
resultado = leer_placa_desde_imagen("imagenes/captura_actual.jpg")

if resultado["estado"] == "OK":
    placa = resultado["placa"]
else:
    placa = input("Digite la placa manualmente: ")
```

---

## Recomendación final

No eliminar el ingreso manual de placa. Debe quedar como respaldo si:

```text
- la cámara falla,
- YOLO no detecta placa,
- EasyOCR no lee bien el texto,
- la imagen tiene mala iluminación o movimiento.
```
