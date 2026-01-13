import serial
import time

# ============================================================================
# KONFIGURASI SERIAL
# ============================================================================
PORT = 'COM11'  # Sesuaikan dengan port kamu
BAUD = 115200

# ============================================================================
# KONFIGURASI TEST
# ============================================================================
STEP_DEGREE = 15  # Increment derajat (5, 10, 15, 30, 45, dll)
DELAY_BETWEEN = 2  # Delay antar broadcast (detik)

# ============================================================================
# FUNGSI KONVERSI
# ============================================================================
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
    
    byte_high = (digital >> 8) & 0xFF
    byte_low = digital & 0xFF
    return f"0x{byte_high:02X}", f"0x{byte_low:02X}"

# ============================================================================
# FUNGSI BROADCAST
# ============================================================================
def create_broadcast(device_config):
    """
    Create 15-byte broadcast packet
    
    device_config: dict dengan key 1-5 dan value degree
    Contoh: {1: 90, 3: 180, 5: 270} -> device 1=90°, 3=180°, 5=270°, sisanya 0
    """
    header = ["0xA5", "0x99"]
    reserved = ["0x00", "0x00", "0x00"]
    
    device_data = []
    for dev in range(1, 6):
        if dev in device_config:
            hex_high, hex_low = degree_to_hex(device_config[dev], device_id=dev)
            device_data.extend([hex_high, hex_low])
        else:
            device_data.extend(["0x00", "0x00"])
    
    return header + reserved + device_data

def send_broadcast(ser, packet, device_config):
    """Send broadcast and display info"""
    # Convert hex strings to binary bytes
    binary_data = bytes([int(x, 16) for x in packet])
    ser.write(binary_data)
    
    # Display info
    active_devices = [f"#{dev}={deg}°" for dev, deg in device_config.items()]
    print(f"[OK] Sent: {', '.join(active_devices)}")
    print(f"  Packet (HEX): {' '.join(packet)}")
    print(f"  Packet (BIN): {binary_data.hex(' ').upper()}")
    
    # Wait for response
    time.sleep(0.1)
    while ser.in_waiting > 0:
        response = ser.readline().decode().strip()
        print(f"  ← {response}")

# ============================================================================
# MODE TESTING
# ============================================================================
def mode_single_device():
    """Test satu device dengan auto-increment"""
    print("\n=== SINGLE DEVICE MODE ===")
    device_id = int(input("Pilih device (1-5): "))
    
    if device_id < 1 or device_id > 5:
        print("❌ Device harus 1-5!")
        return None
    
    return {
        'mode': 'single',
        'devices': [device_id],
        'description': f"Device #{device_id}"
    }

def mode_multiple_devices():
    """Test beberapa device dengan nilai yang sama"""
    print("\n=== MULTIPLE DEVICES MODE ===")
    print("Masukkan device yang ingin ditest (pisahkan dengan koma)")
    print("Contoh: 1,3,5 atau 2,4")
    
    devices_input = input("Device: ")
    devices = [int(d.strip()) for d in devices_input.split(',')]
    
    # Validasi
    if not all(1 <= d <= 5 for d in devices):
        print("❌ Semua device harus 1-5!")
        return None
    
    return {
        'mode': 'multiple',
        'devices': devices,
        'description': f"Devices: {', '.join([f'#{d}' for d in devices])}"
    }

def mode_all_devices():
    """Test semua 5 device bersamaan"""
    print("\n=== ALL DEVICES MODE ===")
    print("Semua device (1-5) akan ditest dengan nilai yang sama")
    
    return {
        'mode': 'all',
        'devices': [1, 2, 3, 4, 5],
        'description': "All Devices (#1-#5)"
    }

def mode_custom():
    """Set nilai berbeda untuk setiap device"""
    print("\n=== CUSTOM MODE ===")
    print("Set nilai awal untuk setiap device (kosongkan untuk skip)")
    
    device_config = {}
    for dev in range(1, 6):
        value = input(f"Device #{dev} start degree (0-360, Enter=skip): ")
        if value.strip():
            device_config[dev] = int(value)
    
    if not device_config:
        print("❌ Minimal satu device harus diisi!")
        return None
    
    return {
        'mode': 'custom',
        'custom_config': device_config,
        'description': f"Custom: {', '.join([f'#{d}={v}°' for d, v in device_config.items()])}"
    }

# ============================================================================
# MAIN PROGRAM
# ============================================================================
def main():
    print("="*70)
    print("  AUTO TEST - FLEXIBLE DEVICE SELECTOR")
    print("="*70)
    print("\nPilih mode testing:")
    print("1. Single Device    - Test 1 device (auto-increment 0-360°)")
    print("2. Multiple Devices - Test beberapa device (nilai sama)")
    print("3. All Devices      - Test semua 5 device (nilai sama)")
    print("4. Custom           - Set nilai berbeda per device")
    print("5. Exit")
    
    choice = input("\nPilih mode (1-5): ")
    
    if choice == '1':
        config = mode_single_device()
    elif choice == '2':
        config = mode_multiple_devices()
    elif choice == '3':
        config = mode_all_devices()
    elif choice == '4':
        config = mode_custom()
    elif choice == '5':
        print("Bye!")
        return
    else:
        print("❌ Pilihan tidak valid!")
        return
    
    if config is None:
        return
    
    try:
        # Connect to serial
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"\n[OK] Connected to {PORT} at {BAUD} baud")
        time.sleep(2)
        
        # Clear initial messages
        while ser.in_waiting > 0:
            ser.readline()
        
        print("\n" + "="*70)
        print(f"  TEST MODE: {config['description']}")
        print(f"  Step: {STEP_DEGREE}° | Delay: {DELAY_BETWEEN}s")
        print("="*70)
        print("\nPress Ctrl+C to stop\n")
        
        # Auto-increment loop
        if config['mode'] == 'custom':
            # Custom mode: increment each device independently
            degree = 0
            while degree <= 360:
                print(f"\n[Step {degree // STEP_DEGREE + 1}] Degree: {degree}°")
                print("-" * 70)
                
                # Update all custom devices with current degree
                device_config = {dev: (start + degree) % 361 
                                for dev, start in config['custom_config'].items()}
                
                packet = create_broadcast(device_config)
                send_broadcast(ser, packet, device_config)
                
                degree += STEP_DEGREE
                
                if degree <= 360:
                    print(f"\nWaiting {DELAY_BETWEEN}s before next step...")
                    time.sleep(DELAY_BETWEEN)
        else:
            # Single/Multiple/All mode: same value for all selected devices
            degree = 0
            while degree <= 360:
                print(f"\n[Step {degree // STEP_DEGREE + 1}] Degree: {degree}°")
                print("-" * 70)
                
                # Create config with same degree for all selected devices
                device_config = {dev: degree for dev in config['devices']}
                
                packet = create_broadcast(device_config)
                send_broadcast(ser, packet, device_config)
                
                degree += STEP_DEGREE
                
                if degree <= 360:
                    print(f"\nWaiting {DELAY_BETWEEN}s before next step...")
                    time.sleep(DELAY_BETWEEN)
        
        print("\n" + "="*70)
        print("[OK] Test completed! Full rotation done.")
        print("="*70)
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial Error: {e}")
        print(f"Pastikan port {PORT} benar dan tidak digunakan program lain!")
    except KeyboardInterrupt:
        print("\n\n[OK] Test stopped by user")
        if 'ser' in locals() and ser.is_open:
            ser.close()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
