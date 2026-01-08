import serial
import time

# Konfigurasi serial port
PORT = 'COM11'  # Sesuaikan dengan port kamu
BAUD = 115200

def parse_hex_input(input_str):
    """Parse input HEX dan validasi"""
    parts = input_str.strip().split()
    hex_values = []
    
    for part in parts:
        # Tambahkan 0x jika belum ada
        if not part.startswith('0x') and not part.startswith('0X'):
            part = '0x' + part
        
        try:
            # Validasi HEX
            val = int(part, 16)
            if val < 0 or val > 255:
                return None, f"Nilai {part} harus 0x00-0xFF!"
            hex_values.append(part)
        except ValueError:
            return None, f"Format HEX salah: {part}"
    
    return hex_values, None

def send_broadcast(ser, hex_values):
    """Kirim broadcast 15 bytes ke semua device"""
    if len(hex_values) != 15:
        print(f"❌ Error: Harus 15 byte HEX! (kamu input {len(hex_values)} byte)")
        return False
    
    # Validasi header
    if hex_values[0].upper() != '0XA5' or hex_values[1].upper() != '0X99':
        print(f"❌ Error: Header harus 0xA5 0x99! (kamu input {hex_values[0]} {hex_values[1]})")
        return False
    
    # Kirim data
    data = " ".join(hex_values) + "\n"
    ser.write(data.encode())
    print(f"\n✓ Broadcast sent (15 bytes):")
    print(f"  {data.strip()}")
    time.sleep(0.3)
    
    # Baca response dari semua device
    print("\n📡 Response dari devices:")
    while ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"  ← {response}")
    
    return True

try:
    # Buka koneksi serial
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"✓ Connected to {PORT} at {BAUD} baud\n")
    time.sleep(2)
    
    # Baca pesan awal dari device
    while ser.in_waiting > 0:
        msg = ser.readline().decode().strip()
        print(f"← {msg}")
    
    print("\n" + "="*70)
    print("  DSC-STM BROADCAST CONTROLLER V2")
    print("="*70)
    print("\nProtokol 15-Byte:")
    print("  Byte 1-2   : Header (0xA5 0x99) - WAJIB!")
    print("  Byte 3-5   : Reserved (0x00 0x00 0x00)")
    print("  Byte 6-15  : Device data (2 byte × 5 devices)")
    print("\nFormat:")
    print("  0xA5 0x99 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH")
    print("  └─────────┘ └───────────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘")
    print("    Header      Reserved    Dev#1   Dev#2   Dev#3   Dev#4   Dev#5")
    print("\nContoh:")
    print("  0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF")
    print("  (Dev#1=0°, Dev#2=90°, Dev#3=180°, Dev#4=270°, Dev#5=360°)")
    print("="*70)
    
    # Loop utama
    while True:
        try:
            print("\n" + "-"*70)
            input_str = input("\nInput 15 byte HEX (atau 'q' untuk quit): ").strip()
            
            if input_str.lower() == 'q':
                break
            
            # Parse input
            hex_values, error = parse_hex_input(input_str)
            
            if error:
                print(f"❌ Error: {error}")
                continue
            
            # Kirim broadcast
            send_broadcast(ser, hex_values)
            
        except KeyboardInterrupt:
            print("\n\n✓ Interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    ser.close()
    print("\n✓ Connection closed")
    
except serial.SerialException as e:
    print(f"❌ Error: {e}")
    print(f"Pastikan port {PORT} benar dan tidak digunakan program lain!")
except KeyboardInterrupt:
    print("\n\n✓ Interrupted by user")
    if 'ser' in locals() and ser.is_open:
        ser.close()
