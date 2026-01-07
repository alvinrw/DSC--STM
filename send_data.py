import serial
import time

# Konfigurasi serial port
PORT = 'COM11'  # Sesuaikan dengan port kamu
BAUD = 115200

def send_broadcast(ser, values):
    """Kirim broadcast initialization untuk semua device"""
    # Format: "036 078 120 045 360"
    data = " ".join([str(v).zfill(3) for v in values]) + "\n"
    ser.write(data.encode())
    print(f"✓ Broadcast sent: {data.strip()}")
    time.sleep(0.3)
    
    # Baca response dari semua device
    while ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"  ← {response}")

def send_device_command(ser, device_id, value):
    """Kirim command ke device tertentu"""
    # Kirim device ID
    ser.write(f"#{device_id}\n".encode())
    time.sleep(0.1)
    
    # Kirim value
    ser.write(f"{value}\n".encode())
    print(f"✓ Sent to Device #{device_id}: {value}")
    time.sleep(0.2)
    
    # Baca response
    while ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"  ← {response}")

def main_menu():
    """Tampilkan menu update"""
    print("\n" + "="*50)
    print("  UPDATE DEVICE")
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
    print("  INISIALISASI AWAL - BROADCAST")
    print("="*50)
    print("Masukkan 5 nilai (0-360) untuk Device 1-5")
    print("Contoh: 36 78 120 45 360")
    print("="*50)
    
    while True:
        try:
            values_str = input("\nInput 5 nilai: ").strip()
            values = [int(v) for v in values_str.split()]
            
            if len(values) != 5:
                print("❌ Error: Harus 5 nilai!")
                continue
            
            # Validasi range
            valid = True
            for i, v in enumerate(values):
                if v < 0 or v > 360:
                    print(f"❌ Error: Nilai {i+1} ({v}) harus 0-360!")
                    valid = False
                    break
            
            if not valid:
                continue
            
            # Kirim broadcast
            send_broadcast(ser, values)
            print("\n✓ Inisialisasi selesai!\n")
            break
            
        except ValueError:
            print("❌ Error: Input harus angka!")
    
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
            try:
                values_str = input("Masukkan 5 nilai (0-360): ").strip()
                values = [int(v) for v in values_str.split()]
                
                if len(values) != 5:
                    print("❌ Error: Harus 5 nilai!")
                    continue
                
                # Validasi range
                valid = True
                for i, v in enumerate(values):
                    if v < 0 or v > 360:
                        print(f"❌ Error: Nilai {i+1} harus 0-360!")
                        valid = False
                        break
                
                if not valid:
                    continue
                
                send_broadcast(ser, values)
                
            except ValueError:
                print("❌ Error: Input harus angka!")
        
        elif choice in ['1', '2', '3', '4', '5']:
            # Update device tertentu
            device_id = int(choice)
            print(f"\n--- Update Device #{device_id} ---")
            
            try:
                value = int(input(f"Masukkan nilai (0-360) untuk Device #{device_id}: "))
                
                if value < 0 or value > 360:
                    print("❌ Error: Nilai harus 0-360!")
                    continue
                
                send_device_command(ser, device_id, value)
                
            except ValueError:
                print("❌ Error: Input harus angka!")
        
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
