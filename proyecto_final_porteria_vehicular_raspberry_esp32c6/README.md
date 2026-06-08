# Proyecto final: Sistema de portería vehicular

## Descripción

Sistema embebido de portería vehicular desarrollado con una **Raspberry Pi 400 con Linux** y un **ESP32-C6 programado con ESP-IDF**.

El sistema permite registrar personas, asociarlas a vehículos, validar placas, controlar eventos de entrada y salida, guardar historial en una base de datos SQLite, controlar si un vehículo está actualmente **DENTRO** o **FUERA** del parqueadero y capturar imágenes con una cámara USB asociadas a cada evento.

## Componentes principales

* Raspberry Pi 400 con Linux.
* ESP32-C6.
* Cámara USB Logitech 720p.
* Botones físicos para ENTRADA y SALIDA.
* LED RGB del ESP32-C6 como indicador visual.
* Base de datos SQLite.
* Comunicación serial USB entre ESP32-C6 y Raspberry Pi.
* Python para la lógica principal en la Raspberry Pi.
* ESP-IDF para el firmware del ESP32-C6.

## Funcionalidades implementadas

### ESP32-C6

* Lectura de botones físicos de ENTRADA y SALIDA.
* Envío de eventos en formato JSON hacia la Raspberry Pi.
* Recepción de respuestas desde la Raspberry Pi.
* Indicador RGB para mostrar estados del sistema.
* Comunicación serial por USB.

### Raspberry Pi

* Recepción de eventos por puerto serial.
* Captura automática de imagen al recibir un evento de ENTRADA o SALIDA.
* Solicitud manual de placa.
* Validación de placa en SQLite.
* Registro de personas.
* Registro de vehículos.
* Asociación persona ↔ vehículo.
* Registro de eventos.
* Control de estado DENTRO/FUERA.
* Alertas de entrada duplicada.
* Alertas de salida sin entrada activa.
* Consulta de historial.
* Consulta de eventos con imagen asociada.
* Menú principal unificado.

- Reconocimiento automático de placas desde imagen capturada.
- Detección de placa usando modelo YOLO.
- Lectura OCR de placa usando EasyOCR.
- Limpieza del texto detectado para comparación con SQLite.
- Respaldo manual si la placa no se detecta automáticamente.

## Estructura general del proyecto

```text
proyecto_final_porteria_vehicular_raspberry_esp32c6/
├── app/
│   ├── main.py
│   ├── menu_principal.py
│   ├── gestionar_personas_vehiculos.py
│   ├── consultar_historial.py
│   ├── camara_usb.py
│   ├── probar_camara_evento.py
│   ├── inicializar_bd.py
│   ├── migrar_bd_personas.py
│   ├── migrar_bd_estado.py
│   ├── leer_esp32_json.py
│   ├── responder_esp32_json.py
│   ├── listar_puertos.py
│   └── prueba_entorno.py
│
├── data/
│   └── porteria.db
│
├── firmware_esp32/
│   └── porteria_esp32c6/
│       ├── main/
│       │   ├── main.c
│       │   ├── CMakeLists.txt
│       │   └── idf_component.yml
│       ├── CMakeLists.txt
│       └── sdkconfig
│
├── imagenes/
│   ├── eventos/
│   └── pruebas_camara/
│
├── logs/
├── docs/
├── tests/
└── requirements.txt
```

> Nota: la base de datos, las imágenes reales y archivos generados durante ejecución no se suben al repositorio cuando están excluidos por `.gitignore`.

## Comando principal del sistema

Para ejecutar el sistema desde la Raspberry Pi:

```bash
cd ~/proyecto_porteria
source .venv/bin/activate
python app/menu_principal.py
```

Este comando abre el menú principal del proyecto.

## Menú principal

Al ejecutar:

```bash
python app/menu_principal.py
```

aparece un menú como este:

```text
SISTEMA DE PORTERÍA VEHICULAR - MENÚ PRINCIPAL

1. Iniciar sistema de portería
2. Gestionar personas y vehículos
3. Consultar historial y estados
4. Verificar archivos principales
5. Salir
```

### Opción 1: Iniciar sistema de portería

Ejecuta el sistema principal de control de entrada y salida.

Archivo usado:

```bash
app/main.py
```

Permite:

* Escuchar eventos enviados por el ESP32-C6.
* Detectar si se presionó ENTRADA o SALIDA.
* Capturar una imagen con la cámara USB.
* Solicitar placa manualmente.
* Validar la placa en la base de datos.
* Controlar si el vehículo está DENTRO o FUERA.
* Guardar el evento en SQLite.
* Enviar respuesta al ESP32-C6.

También se puede ejecutar directamente con:

```bash
python app/main.py
```

### Opción 2: Gestionar personas y vehículos

Ejecuta el gestor de personas y vehículos.

Archivo usado:

```bash
app/gestionar_personas_vehiculos.py
```

Permite:

* Registrar una persona.
* Registrar un vehículo.
* Asociar una persona con un vehículo.
* Listar personas con sus vehículos.
* Buscar vehículos por placa.

También se puede ejecutar directamente con:

```bash
python app/gestionar_personas_vehiculos.py
```

### Opción 3: Consultar historial y estados

Ejecuta el módulo de consulta de historial.

Archivo usado:

```bash
app/consultar_historial.py
```

Permite consultar:

* Últimos eventos registrados.
* Eventos por placa.
* Vehículos actualmente DENTRO.
* Vehículos actualmente FUERA.
* Alertas registradas.
* Eventos con imagen asociada.
* Resumen general del sistema.

También se puede ejecutar directamente con:

```bash
python app/consultar_historial.py
```

### Opción 4: Verificar archivos principales

Revisa que existan los archivos principales del proyecto:

* Sistema de portería.
* Gestor de personas y vehículos.
* Consulta de historial.
* Base de datos SQLite.

Esta opción sirve para confirmar rápidamente que la estructura principal del proyecto está completa.

### Opción 5: Salir

Cierra el menú principal.

## Comandos útiles

### Activar entorno virtual

```bash
cd ~/proyecto_porteria
source .venv/bin/activate
```

### Ejecutar menú principal

```bash
python app/menu_principal.py
```

### Ejecutar sistema de portería directamente

```bash
python app/main.py
```

### Gestionar personas y vehículos

```bash
python app/gestionar_personas_vehiculos.py
```

### Consultar historial

```bash
python app/consultar_historial.py
```

### Probar cámara USB

```bash
python app/probar_camara_evento.py
```

### Ver puertos seriales disponibles

```bash
python app/listar_puertos.py
```

### Abrir base de datos SQLite manualmente

```bash
sqlite3 data/porteria.db
```

Dentro de SQLite, algunos comandos útiles son:

```sql
.tables
```

```sql
SELECT * FROM vehiculos;
```

```sql
SELECT * FROM personas;
```

```sql
SELECT * FROM estado_vehiculos;
```

```sql
SELECT id_evento, fecha_hora, evento, placa, estado, imagen
FROM eventos
ORDER BY id_evento DESC
LIMIT 10;
```

Para salir de SQLite:

```sql
.exit
```

## Cámara USB

La cámara USB Logitech 720p fue detectada en Linux como cámara UVC.

Dispositivo usado:

```text
/dev/video0
```

Resolución recomendada:

```text
1280x720
```

Comando base usado para captura:

```bash
fswebcam -d /dev/video0 -r 1280x720 --skip 20 --delay 2 --no-banner archivo.jpg
```

El sistema usa esta configuración para evitar capturas corruptas al inicio y permitir que la cámara estabilice la imagen.

Las imágenes de eventos se guardan en:

```text
imagenes/eventos/
```

Ejemplo de nombre de imagen:

```text
evento_ENTRADA_BBB111_2026_06_05_20_15_07.jpg
```

## Base de datos

La base de datos usada es:

```text
data/porteria.db
```

Tablas principales:

```text
personas
vehiculos
eventos
estado_vehiculos
```

### Tabla personas

Guarda información de las personas registradas.

Ejemplos de datos:

* Documento.
* Nombre.
* Celular.
* Tipo de persona.

### Tabla vehiculos

Guarda información de vehículos registrados.

Ejemplos de datos:

* Placa.
* Tipo de vehículo.
* Color.
* Estado activo/inactivo.
* Persona asociada.

### Tabla eventos

Guarda cada evento de entrada o salida.

Ejemplos de datos:

* Fecha y hora.
* Tipo de evento.
* Placa.
* Estado de autorización.
* Detalle.
* Imagen asociada.
* Persona asociada.

### Tabla estado_vehiculos

Controla si un vehículo está actualmente:

```text
DENTRO
FUERA
```

Esta tabla permite evitar entradas duplicadas y salidas sin entrada activa.

## Flujo actual del sistema

```text
Botón ENTRADA/SALIDA en ESP32-C6
↓
ESP32-C6 envía evento JSON a Raspberry Pi
↓
Raspberry Pi recibe el evento
↓
Raspberry Pi captura imagen automáticamente
↓
Raspberry Pi intenta detectar y leer la placa automáticamente
↓
Si detecta placa:
    usa la placa automática
Si no detecta placa:
    solicita ingreso manual
↓
Raspberry Pi valida la placa final en SQLite
↓
Raspberry Pi guarda evento e imagen
↓
Raspberry Pi responde al ESP32-C6
↓
ESP32-C6 muestra el estado con LED RGB

## Lógica DENTRO/FUERA

### Entrada válida

```text
Vehículo registrado + estado FUERA
→ AUTORIZADO
→ estado cambia a DENTRO
```

### Entrada duplicada

```text
Vehículo registrado + estado DENTRO
→ NO_AUTORIZADO
→ alerta de entrada duplicada
```

### Salida válida

```text
Vehículo registrado + estado DENTRO
→ AUTORIZADO
→ estado cambia a FUERA
```

### Salida sin entrada activa

```text
Vehículo registrado + estado FUERA
→ NO_AUTORIZADO
→ alerta de salida sin entrada activa
```

### Placa no registrada

```text
Placa no existe o está inactiva
→ NO_AUTORIZADO
```

## Estado actual del desarrollo

Último paso completado:

```text
Paso 24: Reconocimiento automático de placas integrado al flujo principal
```

Funcionalidades completadas hasta este punto:

* Comunicación ESP32-C6 ↔ Raspberry Pi.
* Botones físicos de ENTRADA y SALIDA.
* LED RGB como indicador. 
* Base de datos SQLite.
* Registro de personas.
* Registro de vehículos.
* Asociación persona ↔ vehículo.
* Validación de placas.
* Control DENTRO/FUERA.
* Captura automática con cámara USB.
* Guardado de ruta de imagen en SQLite.
* Consulta de historial con imágenes.
* Menú principal unificado.


## Próximo desarrollo

```text
Paso 26: Mejorar historial para indicar si la placa fue automática o manual

## Flujo futuro esperado

```text
Botón ENTRADA/SALIDA
↓
Captura automática de imagen
↓
Modelo intenta detectar placa
↓
Si detecta placa:
    valida automáticamente
Si no detecta placa:
    solicita ingreso manual
↓
Guarda evento con placa final e imagen
```

Más adelante se podrá agregar una opción para que el guarda edite la placa si el sistema la detecta incorrectamente.

## Autor

Proyecto desarrollado como trabajo final para la materia **Programación de Sistemas Embebidos Linux**.
