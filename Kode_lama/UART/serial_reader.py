import serial
import time
from datetime import datetime

# Konfigurasi serial port
PORT = 'COM17'  # Sesuaikan dengan port kamu
BAUD = 115200

def parse_broadcast_response(line):
    """Parse response dari STM32"""
    # Cek apakah ini adalah data broadcast yang diterima
    if "Broadcast received" in line:
        return "BROADCAST", line
    elif "Device" in line and "Digital:" in line:
        # Format: Device X - Digital: XXXXX, Syncro: XXX.XX deg
        try:
            parts = line.split('-')
            device_part = parts[0].strip()
            data_part = parts[1].strip()
            
            device_num = device_part.split()[1]
            
            digital_val = data_part.split(',')[0].split(':')[1].strip()
            syncro_val = data_part.split(',')[1].split(':')[1].strip()
            
            return "DEVICE_DATA", {
                'device': device_num,
                'digital': digital_val,
                'syncro': syncro_val
            }
        except:
            return "UNKNOWN", line
    elif "Invalid" in line or "Error" in line:
        return "ERROR", line
    else:
        return "INFO", line

def format_output(msg_type, data):
    """Format output dengan timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    if msg_type == "BROADCAST":
        return f"[{timestamp}] 📡 {data}"
    elif msg_type == "DEVICE_DATA":
        return f"[{timestamp}] 📊 Device #{data['device']} → Digital: {data['digital']}, Syncro: {data['syncro']}"
    elif msg_type == "ERROR":
        return f"[{timestamp}] ❌ {data}"
    elif msg_type == "INFO":
        return f"[{timestamp}] ℹ️  {data}"
    else:
        return f"[{timestamp}] {data}"

try:
    # Buka koneksi serial
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"✓ Connected to {PORT} at {BAUD} baud")
    print(f"✓ Listening for data from STM32...")
    print("=" * 80)
    print("Press Ctrl+C to stop\n")
    
    time.sleep(2)
    
    # Bersihkan buffer awal
    ser.reset_input_buffer()
    
    # Loop membaca data
    while True:
        if ser.in_waiting > 0:
            try:
                # Baca satu baris
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line:  # Jika ada data
                    # Parse dan format output
                    msg_type, data = parse_broadcast_response(line)
                    output = format_output(msg_type, data)
                    print(output)
                    
            except UnicodeDecodeError:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Decode error")
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Parse error: {e}")
        
        time.sleep(0.01)  # Small delay untuk mengurangi CPU usage

except serial.SerialException as e:
    print(f"\n❌ Serial Error: {e}")
    print(f"Pastikan port {PORT} benar dan tidak digunakan program lain!")
except KeyboardInterrupt:
    print("\n\n✓ Stopped by user")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("✓ Connection closed")
