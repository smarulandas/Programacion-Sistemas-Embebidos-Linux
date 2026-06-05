# Registra el componente principal del proyecto.
# main.c será el archivo fuente que se compilará.
# REQUIRES indica las librerías usadas por este componente:
# - led_strip: control del RGB integrado.
# - esp_driver_uart: lectura y escritura por UART/serial.
# - esp_driver_gpio: lectura de botones físicos.
idf_component_register(SRCS "main.c"
                       INCLUDE_DIRS "."
                       REQUIRES led_strip esp_driver_uart esp_driver_gpio)