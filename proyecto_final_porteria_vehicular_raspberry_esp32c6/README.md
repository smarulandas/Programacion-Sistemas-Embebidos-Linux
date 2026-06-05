# Proyecto final: Sistema de portería vehicular

## Descripción

Sistema embebido de portería vehicular usando:

- Raspberry Pi 400 con Linux.
- ESP32-C6 programado con ESP-IDF.
- Comunicación serial USB.
- Base de datos SQLite.
- Python para lógica principal.
- Botones físicos de ENTRADA y SALIDA.
- LED RGB como indicador visual.

## Funcionalidades implementadas

### ESP32-C6

- Lectura de botones físicos.
- Envío de eventos JSON a la Raspberry.
- Recepción de respuestas desde la Raspberry.
- Indicador RGB para estados del sistema.

### Raspberry Pi

- Recepción de eventos por puerto serial.
- Solicitud manual de placa.
- Validación de placa en SQLite.
- Registro de personas.
- Registro de vehículos.
- Asociación persona ↔ vehículo.
- Registro de eventos.
- Control de estado DENTRO/FUERA.
- Alertas de entrada duplicada.
- Alertas de salida sin entrada activa.
- Menú principal unificado.

## Comando principal

