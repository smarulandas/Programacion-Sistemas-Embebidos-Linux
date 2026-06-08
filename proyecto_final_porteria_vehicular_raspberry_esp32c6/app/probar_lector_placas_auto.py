from lector_placas_auto import detectar_placa_automatica


"""
Prueba aislada del lector automático de placas desde la carpeta app.

Esta prueba valida que app/ pueda usar el módulo externo de placas.
"""


def main():
    print("=== Prueba del lector automático de placas ===")

    ruta_imagen = "imagenes/pruebas_camara/prueba_placa_yolo.jpg"

    resultado = detectar_placa_automatica(ruta_imagen)

    print("\n=== Resultado ===")
    print(f"OK: {resultado['ok']}")
    print(f"Estado: {resultado['estado']}")
    print(f"Placa: {resultado['placa']}")
    print(f"Confianza detección: {resultado['confianza_deteccion']}")
    print(f"Confianza OCR: {resultado['confianza_ocr']}")
    print(f"Mensaje: {resultado['mensaje']}")

    if resultado["ok"]:
        print("[OK] Lectura automática funcionando desde app.")
    else:
        print("[ALERTA] No se obtuvo placa automática.")


if __name__ == "__main__":
    main()