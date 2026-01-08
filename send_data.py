import serial
import time

# Konfigurasi serial port
PORT = 'COM11'  # Sesuaikan dengan port kamu
BAUD = 115200

def send_broadcast(ser, hex_values):
    """Kirim broadcast initialization untuk semua device (15 HEX bytes total)"""
    # Format 15 bytes:
    # - Byte 1-2: Header (0xA5 0x99) - WAJIB!
    # - Byte 3-5: Reserved (0x00 0x00 0x00)
    # - Byte 6-15: Device data (10 bytes, 2 per device)
    
    if len(hex_values) != 15:
        print("❌ Error: Harus 15 byte HEX!")
        return
    
    # Kirim sebagai string HEX
    data = " ".join(hex_values) + "\n"
    ser.write(data.encode())
    print(f"✓ Broadcast sent (15 bytes): {data.strip()}")
    time.sleep(0.3)
    
    # Baca response dari semua device
    while ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"  ← {response}")

def send_device_command(ser, device_id, hex_high, hex_low):
    """Kirim command ke device tertentu (2 HEX bytes)"""
    # Kirim device ID
    ser.write(f"#{device_id}\n".encode())
    time.sleep(0.1)
    
    # Kirim 2 bytes HEX
    data = f"{hex_high} {hex_low}\n"
    ser.write(data.encode())
    
    # Hitung 16-bit value untuk display
    val_high = int(hex_high, 16)
    val_low = int(hex_low, 16)
    value_16bit = (val_high << 8) | val_low
    
    print(f"✓ Sent to Device #{device_id}: {hex_high} {hex_low} (16-bit: {value_16bit})")
    time.sleep(0.2)
    
    # Baca response
    while ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"  ← {response}")

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

def main_menu():
    """Tampilkan menu update"""
    print("\n" + "="*50)
    print("  UPDATE DEVICE (HEX MODE)")
    print("="*50)
    print("0. Broadcast (set all 5 devices)")
    print("1. Update Device #1")
    print("2. Update Device #2")
    print("3. Update Device #3")
    print("4. Update Device #4")
    print("5. Update Device #5")
    print("q. Quit")
    print("="*50)

try:
    # Buka koneksi serial
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"✓ Connected to {PORT} at {BAUD} baud\n")
    time.sleep(2)
    
    # Baca pesan awal dari device
    while ser.in_waiting > 0:
        msg = ser.readline().decode().strip()
        print(f"← {msg}")
    
    # ============================================
    # INISIALISASI AWAL (WAJIB)
    # ============================================
    print("\n" + "="*50)
    print("  INISIALISASI AWAL - BROADCAST (HEX)")
    print("="*50)
    print("Masukkan 15 byte HEX (Header + Reserved + Device Data)")
    print("Format: 0xA5 0x99 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH")
    print("Contoh: 0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF")
    print("        └─────────┘ └───────────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘")
    print("          Header      Reserved    Dev1    Dev2    Dev3    Dev4    Dev5")
    print("="*50)
    
    while True:
        try:
            input_str = input("\nInput 15 byte HEX: ").strip()
            hex_values, error = parse_hex_input(input_str)
            
            if error:
                print(f"❌ Error: {error}")
                continue
            
            if len(hex_values) != 15:
                print(f"❌ Error: Harus 15 byte! (kamu input {len(hex_values)} byte)")
                continue
            
            # Kirim broadcast
            send_broadcast(ser, hex_values)
            print("\n✓ Inisialisasi selesai!\n")
            break
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # ============================================
    # MENU UPDATE DEVICE
    # ============================================
    while True:
        main_menu()
        choice = input("\nPilih menu: ").strip()
        
        if choice == 'q' or choice == 'Q':
            break
        
        elif choice == '0':
            # Broadcast ulang
            print("\n--- Broadcast (Set All Devices) ---")
            print("Format: 0xA5 0x99 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH")
            print("Contoh: 0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF")
            try:
                input_str = input("Input 15 byte HEX: ").strip()
                hex_values, error = parse_hex_input(input_str)
                
                if error:
                    print(f"❌ Error: {error}")
                    continue
                
                if len(hex_values) != 15:
                    print(f"❌ Error: Harus 15 byte!")
                    continue
                
                send_broadcast(ser, hex_values)
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice in ['1', '2', '3', '4', '5']:
            # Update device tertentu
            device_id = int(choice)
            print(f"\n--- Update Device #{device_id} ---")
            print("Format: 0xHH 0xHH (2 byte HEX)")
            print("Contoh: 0x80 0x00 (32768 decimal = 180°)")
            
            try:
                input_str = input(f"Input 2 byte HEX untuk Device #{device_id}: ").strip()
                hex_values, error = parse_hex_input(input_str)
                
                if error:
                    print(f"❌ Error: {error}")
                    continue
                
                if len(hex_values) != 2:
                    print(f"❌ Error: Harus 2 byte!")
                    continue
                
                send_device_command(ser, device_id, hex_values[0], hex_values[1])
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        else:
            print("❌ Pilihan tidak valid!")
    
    ser.close()
    print("\n✓ Connection closed")
    
except serial.SerialException as e:
    print(f"❌ Error: {e}")
    print(f"Pastikan port {PORT} benar dan tidak digunakan program lain!")
except KeyboardInterrupt:
    print("\n\n✓ Interrupted by user")
    if 'ser' in locals() and ser.is_open:
        ser.close()
