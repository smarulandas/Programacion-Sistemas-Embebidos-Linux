import serial.tools.list_ports

print("=== Puertos seriales detectados ===")

puertos = serial.tools.list_ports.comports()

if not puertos:
    print("[ERROR] No se detectaron puertos seriales.")
else:
    for puerto in puertos:
        print(f"Dispositivo: {puerto.device}")
        print(f"Descripción: {puerto.description}")
        print(f"Fabricante: {puerto.manufacturer}")
        print("-" * 40)
