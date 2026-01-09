import serial
import time

# Konfigurasi
PORT = 'COM11'  # Sesuaikan dengan port kamu
BAUD = 115200
DEVICE_ID = 3  # Device yang akan ditest (1-5)
STEP_DEGREE = 15  # Increment derajat (bisa diganti: 5, 10, 15, 30, 45, dll)
DELAY_BETWEEN = 2  # Delay antar broadcast (detik)

def degree_to_hex(degree):
    """Convert degree (0-360) to 2-byte HEX"""
    # Formula: HEX = (degree / 360) * 65535
    digital = int((degree / 360.0) * 65535)
    
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
            hex_high, hex_low = degree_to_hex(degree)
            device_data.extend([hex_high, hex_low])
        else:
            # Other devices get 0
            device_data.extend(["0x00", "0x00"])
    
    # Combine all
    full_packet = header + reserved + device_data
    return full_packet

def send_broadcast(ser, packet, degree):
    """Send broadcast and display info"""
    data = " ".join(packet) + "\n"
    ser.write(data.encode())
    
    print(f"✓ Sent: {degree:3d}° → Device #{DEVICE_ID}")
    print(f"  Packet: {data.strip()}")
    
    # Wait for response (optional)
    time.sleep(0.1)
    while ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"  ← {response}")

try:
    # Connect to serial
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"✓ Connected to {PORT} at {BAUD} baud\n")
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
    print("✓ Test completed! Full rotation done.")
    print("="*70)
    
    ser.close()
    
except serial.SerialException as e:
    print(f"❌ Serial Error: {e}")
    print(f"Pastikan port {PORT} benar dan tidak digunakan program lain!")
except KeyboardInterrupt:
    print("\n\n✓ Test stopped by user")
    if 'ser' in locals() and ser.is_open:
        ser.close()
except Exception as e:
    print(f"❌ Error: {e}")
    if 'ser' in locals() and ser.is_open:
        ser.close()
