import serial
import time

# Konfigurasi serial port
PORT = 'COM11'  # Sesuaikan dengan port kamu
BAUD = 115200

try:
    # Buka koneksi serial
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to {PORT} at {BAUD} baud")
    time.sleep(2)  # Tunggu STM32 ready
    
    while True:
        # Input nilai dari user
        try:
            value = input("\nMasukkan nilai (0-360) atau 'q' untuk quit: ")
            
            if value.lower() == 'q':
                break
            
            # Validasi input
            num = int(value)
            if num < 0 or num > 360:
                print("Nilai harus antara 0-360!")
                continue
            
            # Kirim ke STM32 (format: angka + newline)
            data = f"{num}\n"
            ser.write(data.encode())
            print(f"✓ Sent: {num}")
            
            # Baca response dari STM32 (jika ada)
            time.sleep(0.1)
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                print(f"← STM32: {response}")
                
        except ValueError:
            print("Input harus angka!")
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break
    
    ser.close()
    print("Connection closed")
    
except serial.SerialException as e:
    print(f"Error: {e}")
    print(f"Pastikan port {PORT} benar dan tidak digunakan program lain!")
