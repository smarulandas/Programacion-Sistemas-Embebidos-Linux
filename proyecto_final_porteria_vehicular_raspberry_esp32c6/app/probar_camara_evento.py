from camara_usb import capturar_imagen_evento


"""
Prueba aislada de cámara USB.

Este archivo prueba que el módulo camara_usb.py pueda:
- Capturar una imagen.
- Guardarla en imagenes/eventos/.
- Retornar la ruta relativa.
"""


def main():
    print("=== Prueba de cámara para eventos ===")

    evento = "ENTRADA"
    placa = "PRUEBA123"

    ruta_imagen = capturar_imagen_evento(evento, placa)

    print("\n=== Resultado ===")
    print(f"Ruta retornada: {ruta_imagen}")

    if ruta_imagen == "SIN_CAMARA":
        print("[ERROR] No se pudo capturar la imagen.")
    else:
        print("[OK] Imagen capturada correctamente.")


if __name__ == "__main__":
    main()