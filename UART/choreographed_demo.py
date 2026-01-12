import serial
import time
import random

# Konfigurasi DEMO
PORT = 'COM11'  # Sesuaikan dengan port kamu
BAUD = 115200
STEP_DEGREE = 45  # Demo: increment lebih besar untuk cepat
DELAY_BETWEEN = 1  # Demo: delay lebih cepat
MAX_STEPS = 3  # Demo: hanya 3 step untuk contoh

# Mode pilihan
MODE = 2  # 1 = Sequential (urut), 2 = Random HEX

def degree_to_hex(degree):
    """Convert degree (0-360) to 2-byte HEX"""
    digital = int((degree / 360.0) * 65535)
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
    """Create 15-byte broadcast packet - Sequential mode"""
    header = ["0xA5", "0x99"]
    reserved = ["0x00", "0x00", "0x00"]
    
    device_data = []
    hex_high, hex_low = degree_to_hex(degree)
    for dev in range(1, 6):
        device_data.extend([hex_high, hex_low])
    
    full_packet = header + reserved + device_data
    return full_packet, [degree] * 5

def create_broadcast_random():
    """Create 15-byte broadcast packet - Random mode"""
    header = ["0xA5", "0x99"]
    reserved = ["0x00", "0x00", "0x00"]
    
    device_data = []
    degrees = []
    for dev in range(1, 6):
        hex_high, hex_low = random_hex()
        device_data.extend([hex_high, hex_low])
        degree = hex_to_degree(hex_high, hex_low)
        degrees.append(degree)
    
    full_packet = header + reserved + device_data
    return full_packet, degrees

def send_broadcast(ser, packet, degrees, step_num):
    """Send broadcast and display info"""
    data = " ".join(packet) + "\n"
    
    print(f"[OK] Sent to ALL Devices:")
    for i, deg in enumerate(degrees, 1):
        print(f"  Device #{i}: {deg:6.2f} deg")
    print(f"  Packet: {data.strip()}")
    print()

# DEMO MODE - Simulasi tanpa serial
print("="*70)
print(f"  DEMO OUTPUT - AUTO TEST ALL DEVICES (1-5)")
if MODE == 1:
    print(f"  Mode: SEQUENTIAL (Urut)")
    print(f"  Step: {STEP_DEGREE}° | Delay: {DELAY_BETWEEN}s")
else:
    print(f"  Mode: RANDOM HEX")
    print(f"  Delay: {DELAY_BETWEEN}s")
print("="*70)
print()

if MODE == 1:
    # Sequential mode demo
    degree = 0
    step_num = 1
    while step_num <= MAX_STEPS:
        print(f"[Step {step_num}] Degree: {degree}°")
        print("-" * 70)
        
        packet, degrees = create_broadcast_sequential(degree)
        send_broadcast(None, packet, degrees, step_num)
        
        degree += STEP_DEGREE
        step_num += 1
        
        if step_num <= MAX_STEPS:
            time.sleep(0.5)  # Demo delay
    
    print("="*70)
    print("[OK] Demo completed!")
    print("="*70)

else:
    # Random mode demo
    for step_num in range(1, MAX_STEPS + 1):
        print(f"[Step {step_num}] Random Values")
        print("-" * 70)
        
        packet, degrees = create_broadcast_random()
        send_broadcast(None, packet, degrees, step_num)
        
        if step_num < MAX_STEPS:
            time.sleep(0.5)  # Demo delay
    
    print("="*70)
    print("[OK] Demo completed!")
    print("="*70)
