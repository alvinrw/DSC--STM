import serial
import time

# Konfigurasi
PORT = 'COM10'  # Sesuaikan dengan port kamu
BAUD = 115200
DEVICE_ID = 1  # Device yang akan ditest (1-5)
STEP_DEGREE = 15  # Increment derajat (bisa diganti: 5, 10, 15, 30, 45, dll)
DELAY_BETWEEN = 2  # Delay antar broadcast (detik)

def degree_to_hex(degree, device_id=1):
    """
    Convert degree to 2-byte HEX based on device encoding
    
    Device 1-4: digital_val = degree * 10
    Device 5: digital_val = (degree + 179.9) * 10 (Relative Course)
    """
    if device_id == 5:
        # Relative Course encoding: (angle + 179.9) * 10
        # Range: -179.9° to +179.9°
        digital = int((degree + 179.9) * 10)
    else:
        # Standard encoding for devices 1-4: angle * 10
        digital = int(degree * 10)
    
    # Ensure within 16-bit range
    digital = max(0, min(65535, digital))
    
    # Split to 2 bytes (high, low)
    byte_high = (digital >> 8) & 0xFF
    byte_low = digital & 0xFF
    
    return f"0x{byte_high:02X}", f"0x{byte_low:02X}"

def create_broadcast(device_id, degree):
    """Create 15-byte broadcast packet"""
    # Header
    header = ["0xA5", "0x99"]
    
    # Reserved
    reserved = ["0x00", "0x00", "0x00"]
    
    # Device data (5 devices, 2 bytes each)
    device_data = []
    for dev in range(1, 6):
        if dev == device_id:
            # Target device gets the degree value
            hex_high, hex_low = degree_to_hex(degree, device_id=device_id)
            device_data.extend([hex_high, hex_low])
        else:
            # Other devices get 0
            device_data.extend(["0x00", "0x00"])
    
    # Combine all
    full_packet = header + reserved + device_data
    return full_packet

def send_broadcast(ser, packet, degree):
    """Send broadcast and display info"""
    # Convert hex strings to binary bytes
    binary_data = bytes([int(x, 16) for x in packet])
    ser.write(binary_data)
    
    print(f"[OK] Sent: {degree:3d} deg -> Device #{DEVICE_ID}")
    print(f"  Packet (HEX): {' '.join(packet)}")
    print(f"  Packet (BIN): {binary_data.hex(' ').upper()}")
    
    # Wait for response (optional)
    time.sleep(0.1)
    while ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"  ← {response}")

try:
    # Connect to serial
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[OK] Connected to {PORT} at {BAUD} baud\n")
    time.sleep(2)
    
    # Clear initial messages
    while ser.in_waiting > 0:
        ser.readline()
    
    print("="*70)
    print(f"  AUTO TEST - Device #{DEVICE_ID}")
    print(f"  Step: {STEP_DEGREE}° | Delay: {DELAY_BETWEEN}s")
    print("="*70)
    print("\nPress Ctrl+C to stop\n")
    
    # Auto-increment loop
    degree = 0
    while degree <= 360:
        print(f"\n[Step {degree // STEP_DEGREE + 1}] Degree: {degree}°")
        print("-" * 70)
        
        # Create and send broadcast
        packet = create_broadcast(DEVICE_ID, degree)
        send_broadcast(ser, packet, degree)
        
        # Increment
        degree += STEP_DEGREE
        
        # Wait before next
        if degree <= 360:
            print(f"\nWaiting {DELAY_BETWEEN}s before next step...")
            time.sleep(DELAY_BETWEEN)
    
    print("\n" + "="*70)
    print("[OK] Test completed! Full rotation done.")
    print("="*70)
    
    ser.close()
    
except serial.SerialException as e:
    print(f"[ERROR] Serial Error: {e}")
    print(f"Pastikan port {PORT} benar dan tidak digunakan program lain!")
except KeyboardInterrupt:
    print("\n\n[OK] Test stopped by user")
    if 'ser' in locals() and ser.is_open:
        ser.close()
except Exception as e:
    print(f"[ERROR] Error: {e}")
    if 'ser' in locals() and ser.is_open:
        ser.close()