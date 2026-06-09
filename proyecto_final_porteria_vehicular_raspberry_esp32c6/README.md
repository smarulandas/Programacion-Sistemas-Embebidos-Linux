# Sistema de Portería Vehicular con Raspberry Pi 400, ESP32-C6 y Reconocimiento de Placas

## 1. Descripción general

Este proyecto implementa un sistema embebido de portería vehicular usando una Raspberry Pi 400 con Linux, un microcontrolador ESP32-C6, una cámara USB, una base de datos SQLite y un módulo de reconocimiento automático de placas.

El sistema permite registrar eventos de entrada y salida de vehículos, capturar una imagen del evento, intentar reconocer automáticamente la placa mediante YOLO y EasyOCR, validar la placa contra una base de datos local y responder al ESP32-C6 para indicar si el acceso fue autorizado o no autorizado.

Además, el sistema incluye un respaldo manual: si el reconocimiento automático falla, el operador puede ingresar la placa manualmente. También permite registrar una persona y un vehículo cuando una placa nueva intenta ingresar por primera vez.

---

## 2. Componentes utilizados

### Hardware

* Raspberry Pi 400 con Linux
* ESP32-C6
* Cámara USB Logitech 720p
* LED RGB o indicadores visuales conectados al ESP32-C6
* Botones físicos para eventos de ENTRADA y SALIDA
* Cable USB para comunicación serial entre Raspberry Pi y ESP32-C6

### Software

* Python 3
* SQLite
* OpenCV
* PySerial
* YOLO / Ultralytics
* EasyOCR
* ESP-IDF
* Visual Studio Code con conexión SSH a la Raspberry Pi

---

## 3. Funcionalidades principales

El sistema permite:

* Recibir eventos físicos desde el ESP32-C6.
* Diferenciar eventos de ENTRADA y SALIDA.
* Capturar una imagen del vehículo con cámara USB.
* Detectar placas automáticamente mediante un modelo YOLO.
* Leer el texto de la placa con EasyOCR.
* Solicitar placa manual si el reconocimiento automático falla.
* Registrar eventos en una base de datos SQLite.
* Guardar imagen asociada a cada evento.
* Renombrar la imagen usando la placa final detectada o ingresada.
* Consultar historial de eventos.
* Consultar vehículos actualmente dentro o fuera.
* Registrar personas y vehículos.
* Autorizar entrada si el vehículo está registrado y se encuentra fuera.
* Autorizar salida si el vehículo está registrado y se encuentra dentro.
* Registrar una placa nueva durante un evento de ENTRADA.
* Bloquear una SALIDA si la placa no está registrada.

---

## 4. Estructura general del proyecto

```text
proyecto_porteria/
├── app/
│   ├── main.py
│   ├── menu_pruebas_sistema.py
│   ├── consultar_historial.py
│   ├── gestionar_personas_vehiculos.py
│   ├── camara_usb.py
│   ├── lector_placas_auto.py
│   ├── inicializar_bd.py
│   ├── migrar_bd_estado.py
│   ├── migrar_bd_personas.py
│   └── migrar_bd_origen_placa.py
│
├── data/
│   └── porteria.db
│
├── firmware_esp32/
│   └── porteria_esp32c6/
│       └── main/
│           └── main.c
│
├── imagenes/
│   ├── eventos/
│   └── pruebas_camara/
│
├── modulos_externos/
│   └── modulo_lectura_placas/
│
└── README.md
```

---

## 5. Activar el entorno virtual

Antes de ejecutar el sistema, se debe activar el entorno virtual de Python:

```bash
cd ~/proyecto_porteria
source .venv/bin/activate
```

La terminal debe mostrar `(.venv)` al inicio. Esto es importante porque el reconocimiento de placas necesita librerías como OpenCV, Torch, Ultralytics y EasyOCR.

---

## 6. Ejecutar el menú principal de pruebas

El proyecto se puede ejecutar desde un menú central:

```bash
python app/menu_pruebas_sistema.py
```

El menú muestra:

```text
1. Ejecutar sistema completo de portería
2. Consultar historial detallado
3. Probar cámara USB
4. Probar reconocimiento automático de placas
5. Ver últimos eventos guardados
6. Gestionar personas y vehículos
0. Salir
```

---

## 7. Opción 1: Ejecutar sistema completo de portería

Esta es la opción principal del proyecto.

Flujo general:

```text
ESP32-C6 detecta botón de ENTRADA o SALIDA
↓
Envía evento por serial a la Raspberry Pi
↓
Raspberry captura una imagen con la cámara USB
↓
Se intenta detectar y leer la placa automáticamente
↓
Si falla el OCR, se solicita la placa manualmente
↓
Se consulta la base de datos SQLite
↓
Se guarda el evento con imagen, placa, estado y origen de placa
↓
Se responde al ESP32-C6 con AUTORIZADO o NO_AUTORIZADO
```

Para ejecutar:

```bash
python app/menu_pruebas_sistema.py
```

Seleccionar:

```text
1
```

---

## 8. Flujo de ENTRADA

### Caso 1: placa registrada y vehículo fuera

Si la placa está registrada y el vehículo aparece como `FUERA`, el sistema autoriza la entrada:

```text
AUTORIZADO:ENTRADA:PLACA
```

Luego actualiza el estado del vehículo a:

```text
DENTRO
```

### Caso 2: placa registrada y vehículo ya dentro

Si el vehículo ya aparece como `DENTRO`, el sistema no autoriza una entrada duplicada.

### Caso 3: placa no registrada

Si la placa no está registrada y el evento es de ENTRADA, el sistema pregunta:

```text
¿Desea registrar esta persona y vehículo ahora? [s/n]
```

Si el operador responde `s`, el sistema solicita:

```text
Documento o identificación
Nombre completo
Celular
Tipo de persona
Tipo de vehículo
Color del vehículo
```

Después registra la persona, registra el vehículo, crea su estado inicial como `FUERA`, revalida la placa y autoriza la entrada si corresponde.

---

## 9. Flujo de SALIDA

### Caso 1: placa registrada y vehículo dentro

Si la placa está registrada y el vehículo aparece como `DENTRO`, el sistema autoriza la salida:

```text
AUTORIZADO:SALIDA:PLACA
```

Luego actualiza el estado del vehículo a:

```text
FUERA
```

### Caso 2: placa registrada pero vehículo fuera

Si el vehículo aparece como `FUERA`, el sistema no autoriza la salida porque no existe una entrada activa.

### Caso 3: placa no registrada

Si se presiona SALIDA y la placa no está registrada, el sistema no permite registrar el vehículo en ese momento. Muestra una alerta:

```text
No se puede registrar una SALIDA para una placa no registrada.
Para salir, el vehículo debe estar registrado y tener una entrada activa.
```

El evento queda guardado como `NO_AUTORIZADO`.

---

## 10. Base de datos SQLite

La base de datos principal está en:

```text
data/porteria.db
```

Tablas principales:

```text
personas
vehiculos
estado_vehiculos
eventos
```

### Tabla personas

Guarda información de las personas asociadas a vehículos.

Campos principales:

```text
id_persona
documento
nombre
celular
tipo_persona
fecha_registro
activo
```

### Tabla vehiculos

Guarda información de los vehículos registrados.

Campos principales:

```text
placa
tipo_vehiculo
color
nombre_conductor
celular
fecha_registro
activo
id_persona
```

### Tabla estado_vehiculos

Guarda si un vehículo está actualmente dentro o fuera.

Campos principales:

```text
placa
estado_actual
id_evento_entrada_actual
fecha_hora_entrada
ultima_actualizacion
```

### Tabla eventos

Guarda cada evento de entrada o salida.

Campos principales:

```text
id_evento
fecha_hora
evento
placa
estado
contador_esp32
origen
detalle
imagen
id_persona
placa_origen
confianza_deteccion
confianza_ocr
```

---

## 11. Consultar últimos eventos

Desde el menú:

```text
5. Ver últimos eventos guardados
```

También se puede consultar directamente con SQLite:

```bash
sqlite3 data/porteria.db "SELECT id_evento, evento, placa, estado, placa_origen, imagen FROM eventos ORDER BY id_evento DESC LIMIT 5;"
```

---

## 12. Consultar historial detallado

Desde el menú:

```text
2. Consultar historial detallado
```

Este módulo permite:

```text
- Ver últimos eventos
- Buscar eventos por placa
- Ver vehículos actualmente DENTRO
- Ver vehículos actualmente FUERA
- Ver alertas
- Ver eventos con imagen
- Ver resumen general
```

---

## 13. Registrar personas y vehículos manualmente

Desde el menú:

```text
6. Gestionar personas y vehículos
```

Opciones disponibles:

```text
1. Registrar persona y vehículo
2. Listar personas con vehículos
3. Buscar vehículo por placa
4. Salir
```

Esta opción sirve para registrar previamente placas autorizadas.

---

## 14. Probar cámara USB

Desde el menú:

```text
3. Probar cámara USB
```

Las imágenes de prueba se guardan en:

```text
imagenes/pruebas_camara/
```

Las imágenes de eventos reales se guardan en:

```text
imagenes/eventos/
```

---

## 15. Probar reconocimiento automático de placas

Desde el menú:

```text
4. Probar reconocimiento automático de placas
```

El sistema toma una imagen existente y ejecuta el módulo de lectura automática.

El resultado puede ser:

```text
OK
SIN_PLACA
OCR_FALLIDO
ERROR
```

Si el modelo falla durante el sistema completo, se solicita placa manual.

---

## 16. Firmware del ESP32-C6

El firmware se encuentra en:

```text
firmware_esp32/porteria_esp32c6/
```

Para compilar:

```bash
cd ~/proyecto_porteria/firmware_esp32/porteria_esp32c6
. ~/esp/esp-idf/export.sh
idf.py build
```

Para flashear:

```bash
idf.py -p /dev/ttyACM0 flash
```

No se recomienda usar `idf.py monitor` mientras se ejecuta `python app/main.py`, porque ambos intentan usar el mismo puerto serial.

---

## 17. Comunicación serial

La Raspberry Pi se comunica con el ESP32-C6 usando:

```text
Puerto: /dev/ttyACM0
Baudrate: 115200
```

El ESP32-C6 envía eventos en formato JSON, por ejemplo:

```json
{
  "origen": "ESP32C6",
  "tipo": "EVENTO_PORTERIA",
  "evento": "ENTRADA",
  "placa": "PENDIENTE_MANUAL",
  "contador": 1
}
```

La Raspberry responde con mensajes como:

```text
AUTORIZADO:ENTRADA:ABC123
NO_AUTORIZADO:SALIDA:XYZ999
```

---

## 18. Consideraciones importantes

* Siempre activar el entorno virtual antes de ejecutar el sistema.
* No abrir `idf.py monitor` al mismo tiempo que el programa Python.
* Si el reconocimiento automático falla, usar ingreso manual de placa.
* El modelo puede fallar si la placa está en una pantalla, con mucho brillo, inclinada, borrosa o muy lejos.
* La entrada de vehículos no registrados permite registro inmediato.
* La salida de vehículos no registrados no permite registro y queda como alerta.
* Si se tarda mucho registrando datos, el ESP32 puede mostrar un aviso de espera agotada, aunque la Raspberry haya guardado correctamente el evento.

---

## 19. Ejecución recomendada para demostración

```bash
cd ~/proyecto_porteria
source .venv/bin/activate
python app/menu_pruebas_sistema.py
```

Luego seleccionar:

```text
1. Ejecutar sistema completo de portería
```

Demostración sugerida:

```text
1. Presionar botón ENTRADA.
2. Mostrar captura de imagen.
3. Mostrar lectura automática o ingreso manual.
4. Mostrar autorización.
5. Consultar últimos eventos guardados.
6. Consultar historial detallado.
7. Mostrar registro de personas y vehículos.
```

---

## 20. Estado final del proyecto

El sistema integra hardware, software, base de datos, visión artificial y comunicación serial para simular una portería vehicular automatizada.

El proyecto cuenta con:

```text
- Comunicación ESP32-C6 ↔ Raspberry Pi
- Captura de imagen por cámara USB
- Reconocimiento automático de placas
- Respaldo manual
- Validación contra SQLite
- Registro de personas y vehículos
- Control de estado DENTRO/FUERA
- Historial de eventos
- Imágenes asociadas a eventos
- Menú de pruebas y demostración
```
