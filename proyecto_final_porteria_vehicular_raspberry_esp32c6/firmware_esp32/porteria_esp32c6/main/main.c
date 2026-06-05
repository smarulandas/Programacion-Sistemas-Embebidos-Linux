#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_log.h"
#include "led_strip.h"
#include "driver/uart.h"
#include "driver/gpio.h"

/*
 * Proyecto: Sistema embebido de portería vehicular
 * Paso 11: Eventos ENTRADA y SALIDA mediante botones físicos
 *
 * En este firmware:
 * - GPIO4 se usa como botón de ENTRADA.
 * - GPIO5 se usa como botón de SALIDA.
 * - El ESP32-C6 envía eventos JSON a la Raspberry Pi.
 * - La Raspberry responde AUTORIZADO o NO_AUTORIZADO.
 * - El RGB integrado cambia de color según el estado.
 *
 * Conexión de botones:
 * GPIO4 ---- botón ENTRADA ---- GND
 * GPIO5 ---- botón SALIDA  ---- GND
 *
 * No se usan resistencias externas porque se activan pull-ups internas.
 */

static const char *TAG = "PORTERIA_ESP32C6";

/* =========================
 * Configuración del RGB
 * ========================= */

#define RGB_GPIO        8
#define RGB_LED_COUNT   1

// Intensidad aproximada del 20%
#define BRILLO_20       51

/* =========================
 * Configuración de botones
 * ========================= */

#define GPIO_BOTON_ENTRADA   4
#define GPIO_BOTON_SALIDA    5

// Con pull-up interno, presionado = 0
#define BOTON_PRESIONADO     0

// Tiempo para evitar rebotes mecánicos del botón
#define TIEMPO_ANTIRREBOTE_MS 250

// Tiempo para que el color del evento se alcance a percibir
#define TIEMPO_COLOR_EVENTO_MS 1200

// Tiempo para que el resultado AUTORIZADO / NO_AUTORIZADO se alcance a percibir
#define TIEMPO_COLOR_RESULTADO_MS 1800

/* =========================
 * Configuración UART
 * ========================= */

#define UART_PORT              UART_NUM_0
#define UART_BAUDRATE          115200
#define UART_RX_BUFFER_SIZE    256

typedef struct {
    const char *nombre;
    uint8_t rojo;
    uint8_t verde;
    uint8_t azul;
} color_rgb_t;

/* =========================
 * Colores de estado
 * ========================= */

static const color_rgb_t COLOR_ESPERA = {
    .nombre = "ESPERA_BLANCO",
    .rojo = 15,
    .verde = 15,
    .azul = 15
};

static const color_rgb_t COLOR_ENTRADA = {
    .nombre = "ENTRADA_AZUL",
    .rojo = 0,
    .verde = 0,
    .azul = BRILLO_20
};

static const color_rgb_t COLOR_SALIDA = {
    .nombre = "SALIDA_MORADO",
    .rojo = 25,
    .verde = 0,
    .azul = BRILLO_20
};

static const color_rgb_t COLOR_AUTORIZADO = {
    .nombre = "AUTORIZADO_VERDE",
    .rojo = 0,
    .verde = BRILLO_20,
    .azul = 0
};

static const color_rgb_t COLOR_NO_AUTORIZADO = {
    .nombre = "NO_AUTORIZADO_ROJO",
    .rojo = BRILLO_20,
    .verde = 0,
    .azul = 0
};

static const color_rgb_t COLOR_PENDIENTE = {
    .nombre = "PENDIENTE_AMARILLO_POLLO",
    .rojo = BRILLO_20,
    .verde = BRILLO_20,
    .azul = 0
};

static led_strip_handle_t rgb_led;

/*
 * Inicializa el RGB integrado.
 */
static void inicializar_rgb(void)
{
    led_strip_config_t strip_config = {
        .strip_gpio_num = RGB_GPIO,
        .max_leds = RGB_LED_COUNT,
        .led_model = LED_MODEL_WS2812,
        .color_component_format = LED_STRIP_COLOR_COMPONENT_FMT_GRB,
        .flags = {
            .invert_out = false
        }
    };

    led_strip_rmt_config_t rmt_config = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 10 * 1000 * 1000,
        .mem_block_symbols = 64,
        .flags = {
            .with_dma = false
        }
    };

    ESP_ERROR_CHECK(led_strip_new_rmt_device(&strip_config, &rmt_config, &rgb_led));
    ESP_ERROR_CHECK(led_strip_clear(rgb_led));
}

/*
 * Cambia el color del RGB integrado.
 */
static void establecer_color_rgb(color_rgb_t color)
{
    ESP_ERROR_CHECK(led_strip_set_pixel(rgb_led, 0, color.rojo, color.verde, color.azul));
    ESP_ERROR_CHECK(led_strip_refresh(rgb_led));
}

/*
 * Inicializa los botones usando pull-up interno.
 *
 * Esto significa:
 * - Sin presionar: el GPIO lee 1.
 * - Presionado: el GPIO se conecta a GND y lee 0.
 */
static void inicializar_botones(void)
{
    gpio_config_t config_botones = {
        .pin_bit_mask = (1ULL << GPIO_BOTON_ENTRADA) | (1ULL << GPIO_BOTON_SALIDA),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };

    ESP_ERROR_CHECK(gpio_config(&config_botones));

    ESP_LOGI(TAG, "Botones inicializados: ENTRADA=GPIO%d, SALIDA=GPIO%d",
             GPIO_BOTON_ENTRADA,
             GPIO_BOTON_SALIDA);
}

/*
 * Inicializa UART0 para leer respuestas desde la Raspberry.
 */
static void inicializar_uart(void)
{
    uart_config_t uart_config = {
        .baud_rate = UART_BAUDRATE,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT
    };

    esp_err_t err = uart_driver_install(
        UART_PORT,
        UART_RX_BUFFER_SIZE * 2,
        0,
        0,
        NULL,
        0
    );

    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Driver UART instalado correctamente.");
    } else if (err == ESP_ERR_INVALID_STATE) {
        ESP_LOGW(TAG, "El driver UART ya estaba instalado. Se continua.");
    } else {
        ESP_ERROR_CHECK(err);
    }

    ESP_ERROR_CHECK(uart_param_config(UART_PORT, &uart_config));

    ESP_ERROR_CHECK(uart_set_pin(
        UART_PORT,
        UART_PIN_NO_CHANGE,
        UART_PIN_NO_CHANGE,
        UART_PIN_NO_CHANGE,
        UART_PIN_NO_CHANGE
    ));
}

/*
 * Envía un evento de portería en formato JSON.
 */
static void enviar_evento_json(const char *evento, const char *placa, int contador)
{
    printf(
        "{\"origen\":\"ESP32C6\",\"tipo\":\"EVENTO_PORTERIA\",\"evento\":\"%s\",\"placa\":\"%s\",\"contador\":%d}\n",
        evento,
        placa,
        contador
    );

    fflush(stdout);
}

/*
 * Procesa la respuesta enviada por la Raspberry.
 */
static void procesar_respuesta(const char *respuesta)
{
    ESP_LOGI(TAG, "RESPUESTA_RASPBERRY: %s", respuesta);

    if (strncmp(respuesta, "AUTORIZADO", 10) == 0) {
        establecer_color_rgb(COLOR_AUTORIZADO);
    } else if (strncmp(respuesta, "NO_AUTORIZADO", 13) == 0) {
        establecer_color_rgb(COLOR_NO_AUTORIZADO);
    } else if (strncmp(respuesta, "PENDIENTE", 9) == 0) {
        establecer_color_rgb(COLOR_PENDIENTE);
    } else {
        ESP_LOGW(TAG, "Respuesta no reconocida: %s", respuesta);
    }
}

/*
 * Lee una línea completa desde UART hasta encontrar '\n'.
 *
 * Esto evita tomar respuestas incompletas o bytes basura.
 * Solo se guardan caracteres ASCII imprimibles.
 */
static bool leer_linea_uart(char *salida, size_t max_len, int timeout_total_ms)
{
    size_t posicion = 0;
    uint8_t caracter;
    int intentos = timeout_total_ms / 20;

    for (int i = 0; i < intentos; i++) {
        int leidos = uart_read_bytes(
            UART_PORT,
            &caracter,
            1,
            pdMS_TO_TICKS(20)
        );

        if (leidos > 0) {
            // Ignora retorno de carro
            if (caracter == '\r') {
                continue;
            }

            // Si llega salto de línea, termina la lectura
            if (caracter == '\n') {
                if (posicion > 0) {
                    salida[posicion] = '\0';
                    return true;
                }
                continue;
            }

            // Solo guarda caracteres imprimibles ASCII
            if (caracter >= 32 && caracter <= 126) {
                if (posicion < max_len - 1) {
                    salida[posicion++] = (char)caracter;
                }
            }
        }
    }

    // Si alcanzó a leer algo, devuelve lo que tenga
    if (posicion > 0) {
        salida[posicion] = '\0';
        return true;
    }

    return false;
}

/*
 * Espera una respuesta completa de la Raspberry.
 *
 * La respuesta debe llegar como una línea terminada en '\n'.
 */
static bool esperar_respuesta_raspberry(void)
{
    char buffer[UART_RX_BUFFER_SIZE];

    bool recibio = leer_linea_uart(buffer, sizeof(buffer), 30000);

    if (recibio) {
        procesar_respuesta(buffer);
        return true;
    }

    ESP_LOGW(TAG, "No se recibio respuesta de la Raspberry.");
    establecer_color_rgb(COLOR_PENDIENTE);
    return false;
}

/*
 * Espera hasta que el botón se suelte.
 *
 * Esto evita que una sola pulsación genere muchos eventos repetidos.
 */
static void esperar_liberacion_boton(gpio_num_t gpio_boton)
{
    while (gpio_get_level(gpio_boton) == BOTON_PRESIONADO) {
        vTaskDelay(pdMS_TO_TICKS(20));
    }

    vTaskDelay(pdMS_TO_TICKS(TIEMPO_ANTIRREBOTE_MS));
}

/*
 * Procesa un evento generado por botón.
 *
 * En este paso ya no se envía una placa fija desde el ESP32-C6.
 * El ESP32 solo indica si el evento es ENTRADA o SALIDA.
 *
 * La placa real será digitada manualmente en la Raspberry Pi.
 */
static void procesar_evento_boton(const char *evento, color_rgb_t color_evento, int contador)
{
    // Muestra el color del evento:
    // ENTRADA -> azul
    // SALIDA  -> morado
    establecer_color_rgb(color_evento);

    ESP_LOGI(TAG, "Boton presionado -> Evento: %s | Contador: %d",
             evento,
             contador);

    // Espera para que el usuario alcance a ver el color del evento
    vTaskDelay(pdMS_TO_TICKS(TIEMPO_COLOR_EVENTO_MS));

    // Limpia respuestas viejas o basura residual antes de enviar un nuevo evento
    uart_flush_input(UART_PORT);

    /*
     * Ahora se envía una placa temporal.
     * La Raspberry reemplazará esta placa por la que el usuario digite.
     */
    enviar_evento_json(evento, "PENDIENTE_MANUAL", contador);

    // Mientras la Raspberry pide la placa, dejamos el RGB en amarillo de espera
    establecer_color_rgb(COLOR_PENDIENTE);

    // Espera la respuesta de la Raspberry
    esperar_respuesta_raspberry();

    // Mantiene visible el resultado antes de volver al estado de espera
    vTaskDelay(pdMS_TO_TICKS(TIEMPO_COLOR_RESULTADO_MS));

    // Vuelve a color de espera
    establecer_color_rgb(COLOR_ESPERA);
}

/*
 * Función principal.
 */
void app_main(void)
{
    ESP_LOGI(TAG, "==================================================");
    ESP_LOGI(TAG, "Sistema de porteria - ESP32-C6 iniciado");
    ESP_LOGI(TAG, "Paso 11: eventos por botones fisicos");
    ESP_LOGI(TAG, "==================================================");

    inicializar_rgb();
    inicializar_botones();
    inicializar_uart();

    establecer_color_rgb(COLOR_ESPERA);

    int contador = 0;

    while (1) {
        /*
         * Botón ENTRADA:
         * Envía placa ABC123, que está registrada en app/main.py.
         * Resultado esperado: AUTORIZADO.
         */
        if (gpio_get_level(GPIO_BOTON_ENTRADA) == BOTON_PRESIONADO) {
            procesar_evento_boton("ENTRADA", COLOR_ENTRADA, contador);
            contador++;
            esperar_liberacion_boton(GPIO_BOTON_ENTRADA);
        }

        /*
         * Botón SALIDA:
         * Envía placa XYZ999, que no está registrada en app/main.py.
         * Resultado esperado: NO_AUTORIZADO.
         */
        if (gpio_get_level(GPIO_BOTON_SALIDA) == BOTON_PRESIONADO) {
            procesar_evento_boton("SALIDA", COLOR_SALIDA, contador);
            contador++;
            esperar_liberacion_boton(GPIO_BOTON_SALIDA);
        }

        // Pequeña espera para no saturar la CPU
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}