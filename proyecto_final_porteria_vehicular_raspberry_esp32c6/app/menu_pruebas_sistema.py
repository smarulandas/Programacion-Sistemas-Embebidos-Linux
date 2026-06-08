import sqlite3
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"
DB_PATH = BASE_DIR / "data" / "porteria.db"
IMAGENES_EVENTOS_DIR = BASE_DIR / "imagenes" / "eventos"
IMAGENES_PRUEBAS_DIR = BASE_DIR / "imagenes" / "pruebas_camara"

sys.path.insert(0, str(APP_DIR))


def limpiar_pantalla():
    print("\n" * 3)


def ejecutar_script(ruta_script):
    if not ruta_script.exists():
        print(f"[ERROR] No existe el archivo: {ruta_script}")
        return

    print(f"[INFO] Ejecutando: {ruta_script}")
    print("[INFO] Para detener, use Ctrl + C si el programa queda esperando eventos.\n")

    try:
        subprocess.run([sys.executable, str(ruta_script)], cwd=str(BASE_DIR))
    except KeyboardInterrupt:
        print("\n[INFO] Ejecución detenida por el usuario.")

def ver_ultimos_eventos():
    print("\n=== Últimos eventos registrados ===")

    if not DB_PATH.exists():
        print(f"[ERROR] No existe la base de datos: {DB_PATH}")
        return

    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            id_evento,
            fecha_hora,
            evento,
            placa,
            estado,
            placa_origen,
            confianza_deteccion,
            confianza_ocr,
            imagen
        FROM eventos
        ORDER BY id_evento DESC
        LIMIT 10
    """)

    filas = cursor.fetchall()
    conexion.close()

    if not filas:
        print("[INFO] No hay eventos registrados.")
        return

    for fila in filas:
        print("-" * 80)
        print(f"ID: {fila['id_evento']}")
        print(f"Fecha/hora: {fila['fecha_hora']}")
        print(f"Evento: {fila['evento']}")
        print(f"Placa: {fila['placa']}")
        print(f"Estado: {fila['estado']}")
        print(f"Origen placa: {fila['placa_origen']}")
        print(f"Confianza YOLO: {fila['confianza_deteccion']:.4f}")
        print(f"Confianza OCR: {fila['confianza_ocr']:.4f}")
        print(f"Imagen: {fila['imagen']}")


def obtener_ultima_imagen():
    imagenes = []

    if IMAGENES_EVENTOS_DIR.exists():
        imagenes.extend(IMAGENES_EVENTOS_DIR.glob("*.jpg"))

    if IMAGENES_PRUEBAS_DIR.exists():
        imagenes.extend(IMAGENES_PRUEBAS_DIR.glob("*.jpg"))

    if not imagenes:
        return None

    imagenes_ordenadas = sorted(
        imagenes,
        key=lambda ruta: ruta.stat().st_mtime,
        reverse=True
    )

    return imagenes_ordenadas[0]


def probar_lector_placas():
    print("\n=== Prueba del lector automático de placas ===")

    try:
        from lector_placas_auto import detectar_placa_automatica
    except Exception as error:
        print("[ERROR] No se pudo importar lector_placas_auto.")
        print(f"[DETALLE] {error}")
        return

    ultima_imagen = obtener_ultima_imagen()

    if ultima_imagen is not None:
        print(f"[INFO] Última imagen encontrada:")
        print(ultima_imagen)
        usar_ultima = input("¿Usar esta imagen? [s/n]: ").strip().lower()

        if usar_ultima == "s":
            ruta_imagen = ultima_imagen
        else:
            texto_ruta = input("Ingrese la ruta de la imagen: ").strip()
            ruta_imagen = Path(texto_ruta)
    else:
        texto_ruta = input("Ingrese la ruta de la imagen: ").strip()
        ruta_imagen = Path(texto_ruta)

    if not ruta_imagen.is_absolute():
        ruta_imagen = BASE_DIR / ruta_imagen

    if not ruta_imagen.exists():
        print(f"[ERROR] La imagen no existe: {ruta_imagen}")
        return

    print("[INFO] Ejecutando YOLO + EasyOCR...")
    resultado = detectar_placa_automatica(str(ruta_imagen))

    print("\n=== Resultado ===")
    print(f"OK: {resultado.get('ok')}")
    print(f"Estado: {resultado.get('estado')}")
    print(f"Placa: {resultado.get('placa')}")
    print(f"Confianza detección: {resultado.get('confianza_deteccion')}")
    print(f"Confianza OCR: {resultado.get('confianza_ocr')}")
    print(f"Mensaje: {resultado.get('mensaje')}")


def mostrar_menu():
    print("\n" + "=" * 70)
    print("MENÚ DE PRUEBAS - SISTEMA DE PORTERÍA VEHICULAR")
    print("=" * 70)
    print("1. Ejecutar sistema completo de portería")
    print("2. Consultar historial detallado")
    print("3. Probar cámara USB")
    print("4. Probar reconocimiento automático de placas")
    print("5. Ver últimos eventos guardados")
    print("0. Salir")
    print("=" * 70)


def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            ejecutar_script(APP_DIR / "main.py")
        elif opcion == "2":
            ejecutar_script(APP_DIR / "consultar_historial.py")
        elif opcion == "3":
            ejecutar_script(APP_DIR / "probar_camara_evento.py")
        elif opcion == "4":
            probar_lector_placas()
        elif opcion == "5":
            ver_ultimos_eventos()
        elif opcion == "0":
            print("[INFO] Saliendo del menú de pruebas.")
            break
        else:
            print("[ERROR] Opción no válida.")

        input("\nPresione Enter para volver al menú...")


if __name__ == "__main__":
    main()