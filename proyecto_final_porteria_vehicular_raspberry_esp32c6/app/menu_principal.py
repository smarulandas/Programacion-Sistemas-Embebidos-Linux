from pathlib import Path
import subprocess
import sys


"""
Proyecto: Sistema embebido de portería vehicular

Paso 18:
Menú principal unificado.

Este archivo permite abrir desde un solo lugar:
1. Sistema de portería en tiempo real.
2. Gestión de personas y vehículos.
3. Consulta de historial.
4. Verificación rápida de archivos principales.
5. Salir.

Este archivo NO reemplaza los otros programas.
Solo los organiza y los ejecuta desde un menú central.
"""


# =========================
# Rutas del proyecto
# =========================

BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"

ARCHIVO_PORTERIA = APP_DIR / "main.py"
ARCHIVO_GESTION = APP_DIR / "gestionar_personas_vehiculos.py"
ARCHIVO_HISTORIAL = APP_DIR / "consultar_historial.py"
ARCHIVO_BD = BASE_DIR / "data" / "porteria.db"


def limpiar_pantalla_visual():
    """
    No borra realmente la terminal.
    Solo imprime espacios para separar visualmente los menús.
    """
    print("\n" * 2)


def pausar():
    """
    Pausa sencilla para que el usuario pueda leer antes de volver al menú.
    """
    input("\nPresiona Enter para volver al menú principal...")


def verificar_archivo(ruta, descripcion):
    """
    Verifica si existe un archivo necesario del sistema.
    """
    if ruta.exists():
        print(f"[OK] {descripcion}: {ruta}")
        return True

    print(f"[ERROR] No se encontró {descripcion}: {ruta}")
    return False


def verificar_archivos_principales():
    """
    Revisa que existan los archivos principales del proyecto.
    """
    limpiar_pantalla_visual()
    print("=" * 80)
    print("VERIFICACIÓN RÁPIDA DEL PROYECTO")
    print("=" * 80)

    todo_ok = True

    todo_ok = verificar_archivo(ARCHIVO_PORTERIA, "Sistema de portería") and todo_ok
    todo_ok = verificar_archivo(ARCHIVO_GESTION, "Gestor de personas y vehículos") and todo_ok
    todo_ok = verificar_archivo(ARCHIVO_HISTORIAL, "Consulta de historial") and todo_ok
    todo_ok = verificar_archivo(ARCHIVO_BD, "Base de datos SQLite") and todo_ok

    print("=" * 80)

    if todo_ok:
        print("[OK] Archivos principales encontrados.")
    else:
        print("[ADVERTENCIA] Falta uno o más archivos. Revisa antes de continuar.")

    pausar()


def ejecutar_programa(ruta_archivo):
    """
    Ejecuta un programa Python hijo.

    Usamos sys.executable para que se use el mismo Python del entorno virtual.
    Es decir, si estás en .venv, ejecutará los otros archivos con ese mismo Python.
    """

    if not ruta_archivo.exists():
        print(f"[ERROR] No existe el archivo: {ruta_archivo}")
        pausar()
        return

    print("\n" + "=" * 80)
    print(f"[INFO] Ejecutando: {ruta_archivo.name}")
    print("[INFO] Cuando salgas de ese programa, volverás al menú principal.")
    print("=" * 80 + "\n")

    try:
        subprocess.run([sys.executable, str(ruta_archivo)], cwd=str(BASE_DIR))

    except KeyboardInterrupt:
        print("\n[INFO] Programa detenido por el usuario.")

    except Exception as error:
        print("[ERROR] Ocurrió un problema ejecutando el programa.")
        print(f"[DETALLE] {error}")

    pausar()


def iniciar_sistema_porteria():
    """
    Abre el sistema principal de portería.

    Este programa usa el puerto serial /dev/ttyACM0.
    Antes de ejecutarlo:
    - El ESP32-C6 debe estar conectado.
    - No debe estar abierto el monitor serial de ESP-IDF.
    """
    limpiar_pantalla_visual()
    print("=" * 80)
    print("INICIAR SISTEMA DE PORTERÍA")
    print("=" * 80)
    print("Antes de continuar verifica:")
    print("1. ESP32-C6 conectado a la Raspberry.")
    print("2. Puerto serial disponible.")
    print("3. No tener abierto idf.py monitor.")
    print("4. Los botones ENTRADA/SALIDA deben estar conectados.")
    print("=" * 80)

    opcion = input("¿Deseas iniciar el sistema de portería? (s/n): ").strip().lower()

    if opcion == "s":
        ejecutar_programa(ARCHIVO_PORTERIA)
    else:
        print("[INFO] Operación cancelada.")
        pausar()


def abrir_gestion_personas_vehiculos():
    """
    Abre el gestor de personas y vehículos.
    """
    ejecutar_programa(ARCHIVO_GESTION)


def abrir_consulta_historial():
    """
    Abre el módulo de consulta de historial.
    """
    ejecutar_programa(ARCHIVO_HISTORIAL)


def mostrar_menu():
    """
    Muestra el menú principal.
    """
    limpiar_pantalla_visual()
    print("=" * 80)
    print("SISTEMA DE PORTERÍA VEHICULAR - MENÚ PRINCIPAL")
    print("=" * 80)
    print("1. Iniciar sistema de portería")
    print("2. Gestionar personas y vehículos")
    print("3. Consultar historial y estados")
    print("4. Verificar archivos principales")
    print("5. Salir")
    print("=" * 80)


def main():
    """
    Ciclo principal del menú.
    """
    while True:
        mostrar_menu()

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            iniciar_sistema_porteria()

        elif opcion == "2":
            abrir_gestion_personas_vehiculos()

        elif opcion == "3":
            abrir_consulta_historial()

        elif opcion == "4":
            verificar_archivos_principales()

        elif opcion == "5":
            print("[INFO] Saliendo del menú principal.")
            break

        else:
            print("[ERROR] Opción no válida.")
            pausar()


if __name__ == "__main__":
    main()