# Programación de Sistemas Embebidos Linux

Repositorio para el desarrollo del proyecto final de la materia **Programación de Sistemas Embebidos Linux**.

## Proyecto incluido

### Sistema de portería vehicular con Raspberry Pi 400 y ESP32-C6

Carpeta principal del proyecto:

```text
proyecto_final_porteria_vehicular_raspberry_esp32c6/
```

## Descripción general

El proyecto consiste en un sistema embebido de portería vehicular desarrollado con una **Raspberry Pi 400 con Linux** y un **ESP32-C6 programado con ESP-IDF**.

El sistema permite controlar eventos de entrada y salida de vehículos, registrar personas, asociarlas a vehículos, validar placas, controlar el estado actual de cada vehículo como **DENTRO** o **FUERA**, guardar eventos en SQLite y capturar imágenes con una cámara USB asociadas a cada evento.

## Estado actual del proyecto

Funcionalidades implementadas hasta el momento:

* Comunicación serial ESP32-C6 ↔ Raspberry Pi.
* Botones físicos para eventos de ENTRADA y SALIDA.
* Indicador RGB en el ESP32-C6.
* Base de datos SQLite.
* Registro de personas.
* Registro de vehículos.
* Asociación persona ↔ vehículo.
* Validación de placas.
* Control de estado DENTRO/FUERA.
* Alertas de entrada duplicada.
* Alertas de salida sin entrada activa.
* Menú principal unificado.
* Cámara USB Logitech 720p integrada.
* Captura automática de imagen por evento.
* Guardado de imágenes en `imagenes/eventos/`.
* Registro de la ruta de imagen en SQLite.
* Historial con rutas de imágenes asociadas.
* Consulta de eventos con imagen asociada.

## Estructura general

```text
programacion-sistemas-embebidos-linux/
│
├── README.md
├── .gitignore
│
└── proyecto_final_porteria_vehicular_raspberry_esp32c6/
    ├── app/
    ├── data/
    ├── docs/
    ├── firmware_esp32/
    ├── imagenes/
    ├── logs/
    ├── tests/
    ├── requirements.txt
    └── README.md
```

## Comando principal del proyecto

Para ejecutar el proyecto desde la Raspberry Pi:

```bash
cd ~/proyecto_porteria
source .venv/bin/activate
python app/menu_principal.py
```

Este comando abre el menú principal del sistema.

## Menú principal

El menú principal permite acceder a las partes más importantes del proyecto:

```text
1. Iniciar sistema de portería
2. Gestionar personas y vehículos
3. Consultar historial y estados
4. Verificar archivos principales
5. Salir
```

### 1. Iniciar sistema de portería

Ejecuta el sistema principal de entrada y salida vehicular.

Permite:

* Recibir eventos del ESP32-C6.
* Capturar una imagen con la cámara USB.
* Solicitar la placa manualmente.
* Validar la placa en SQLite.
* Verificar si el vehículo está DENTRO o FUERA.
* Guardar el evento en la base de datos.
* Enviar respuesta al ESP32-C6.

Comando directo:

```bash
python app/main.py
```

### 2. Gestionar personas y vehículos

Permite administrar los registros principales del sistema.

Permite:

* Registrar personas.
* Registrar vehículos.
* Asociar personas con vehículos.
* Listar personas con sus vehículos.
* Buscar vehículos por placa.

Comando directo:

```bash
python app/gestionar_personas_vehiculos.py
```

### 3. Consultar historial y estados

Permite revisar la información guardada en la base de datos.

Permite consultar:

* Últimos eventos registrados.
* Eventos por placa.
* Vehículos actualmente DENTRO.
* Vehículos actualmente FUERA.
* Alertas registradas.
* Eventos con imagen asociada.
* Resumen general del sistema.

Comando directo:

```bash
python app/consultar_historial.py
```

### 4. Verificar archivos principales

Revisa que existan los archivos principales del proyecto:

* Sistema principal de portería.
* Gestor de personas y vehículos.
* Consulta de historial.
* Base de datos SQLite.

### 5. Salir

Cierra el menú principal.

## Cámara USB

La cámara usada es una **Logitech 720p**, detectada en Linux como cámara UVC.

Dispositivo usado:

```text
/dev/video0
```

Resolución recomendada:

```text
1280x720
```

Comando base probado para captura:

```bash
fswebcam -d /dev/video0 -r 1280x720 --skip 20 --delay 2 --no-banner archivo.jpg
```

Las imágenes asociadas a eventos se guardan en:

```text
imagenes/eventos/
```

## Base de datos

El sistema usa SQLite.

Archivo de base de datos:

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
Raspberry Pi solicita placa manualmente
↓
Raspberry Pi valida la placa en SQLite
↓
Raspberry Pi revisa estado DENTRO/FUERA
↓
Raspberry Pi guarda evento e imagen en SQLite
↓
Raspberry Pi responde al ESP32-C6
↓
ESP32-C6 muestra estado con LED RGB
```

## Próximo desarrollo

El siguiente paso del proyecto será:

```text
Paso 23: Prueba aislada de reconocimiento de placas
```

El objetivo será probar un modelo o sistema de reconocimiento automático de placas usando imágenes guardadas, sin integrarlo todavía al flujo principal.

## Flujo futuro esperado

```text
Botón ENTRADA/SALIDA
↓
Captura automática de imagen
↓
Modelo intenta detectar la placa
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
