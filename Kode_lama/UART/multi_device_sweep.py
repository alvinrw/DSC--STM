import serial
import time
import random

# Konfigurasi
PORT = 'COM11'  # Sesuaikan dengan port kamu
BAUD = 115200
STEP_DEGREE = 15  # Increment derajat untuk mode sequential (5, 10, 15, 30, 45, dll)
DELAY_BETWEEN = 2  # Delay antar broadcast (detik)

# Mode pilihan
MODE = 1  # 1 = Sequential (urut), 2 = Random HEX

def degree_to_hex(degree):
    """Convert degree (0-360) to 2-byte HEX"""
    # Formula: HEX = (degree / 360) * 65535
    digital = int((degree / 360.0) * 65535)
    
    # Split to 2 bytes (high, low)
    byte_high = (digital >> 8) & 0xFF
    byte_low = digital & 0xFF
    
    return f"0x{byte_high:02X}", f"0x{byte_low:02X}"

def random_hex():
    """Generate random 2-byte HEX (0x0000 - 0xFFFF)"""
    value = random.randint(0, 65535)
    byte_high = (value >> 8) & 0xFF
    byte_low = value & 0xFF
    return f"0x{byte_high:02X}", f"0x{byte_low:02X}"

def hex_to_degree(byte_high_str, byte_low_str):
    """Convert HEX string to degree for display"""
    byte_high = int(byte_high_str, 16)
    byte_low = int(byte_low_str, 16)
    digital = (byte_high << 8) | byte_low
    degree = (digital / 65535.0) * 360.0
    return degree

def create_broadcast_sequential(degree):
    """Create 15-byte broadcast packet - Sequential mode (all devices same value)"""
    # Header
    header = ["0xA5", "0x99"]
    
    # Reserved
    reserved = ["0x00", "0x00", "0x00"]
    
    # Device data (5 devices, 2 bytes each) - all get same degree
    device_data = []
    hex_high, hex_low = degree_to_hex(degree)
    for dev in range(1, 6):
        device_data.extend([hex_high, hex_low])
    
    # Combine all
    full_packet = header + reserved + device_data
    return full_packet, [degree] * 5

def create_broadcast_random():
    """Create 15-byte broadcast packet - Random mode (each device gets random value)"""
    # Header
    header = ["0xA5", "0x99"]
    
    # Reserved
    reserved = ["0x00", "0x00", "0x00"]
    
    # Device data (5 devices, 2 bytes each) - each gets random value
    device_data = []
    degrees = []
    for dev in range(1, 6):
        hex_high, hex_low = random_hex()
        device_data.extend([hex_high, hex_low])
        degree = hex_to_degree(hex_high, hex_low)
        degrees.append(degree)
    
    # Combine all
    full_packet = header + reserved + device_data
    return full_packet, degrees

def send_broadcast(ser, packet, degrees, step_num):
    """Send broadcast and display info"""
    data = " ".join(packet) + "\n"
    ser.write(data.encode())
    
    print(f"[OK] Sent to ALL Devices:")
    for i, deg in enumerate(degrees, 1):
        print(f"  Device #{i}: {deg:6.2f} deg")
    print(f"  Packet: {data.strip()}")
    
    # Wait for response (optional)
    time.sleep(0.1)
    while ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"  <- {response}")

try:
    # Connect to serial
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"[OK] Connected to {PORT} at {BAUD} baud\n")
    time.sleep(2)
    
    # Clear initial messages
    while ser.in_waiting > 0:
        ser.readline()
    
    print("="*70)
    print(f"  AUTO TEST - ALL DEVICES (1-5)")
    if MODE == 1:
        print(f"  Mode: SEQUENTIAL (Urut)")
        print(f"  Step: {STEP_DEGREE}° | Delay: {DELAY_BETWEEN}s")
    else:
        print(f"  Mode: RANDOM HEX")
        print(f"  Delay: {DELAY_BETWEEN}s")
    print("="*70)
    print("\nPress Ctrl+C to stop\n")
    
    if MODE == 1:
        # Sequential mode
        degree = 0
        step_num = 1
        while degree <= 360:
            print(f"\n[Step {step_num}] Degree: {degree}°")
            print("-" * 70)
            
            # Create and send broadcast
            packet, degrees = create_broadcast_sequential(degree)
            send_broadcast(ser, packet, degrees, step_num)
            
            # Increment
            degree += STEP_DEGREE
            step_num += 1
            
            # Wait before next
            if degree <= 360:
                print(f"\nWaiting {DELAY_BETWEEN}s before next step...")
                time.sleep(DELAY_BETWEEN)
        
        print("\n" + "="*70)
        print("[OK] Test completed! Full rotation done.")
        print("="*70)
    
    else:
        # Random mode
        step_num = 1
        print("Random mode - Press Ctrl+C to stop\n")
        while True:
            print(f"\n[Step {step_num}] Random Values")
            print("-" * 70)
            
            # Create and send broadcast with random values
            packet, degrees = create_broadcast_random()
            send_broadcast(ser, packet, degrees, step_num)
            
            step_num += 1
            
            # Wait before next
            print(f"\nWaiting {DELAY_BETWEEN}s before next step...")
            time.sleep(DELAY_BETWEEN)
    
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
