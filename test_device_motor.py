#!/usr/bin/env python3
"""
Test Script untuk DSC_rome_device
Mengirim data ke STM32 Device dan menerima feedback untuk verifikasi motor synchro
"""

import serial
import time
import struct

# ============================================
# KONFIGURASI
# ============================================
SERIAL_PORT = 'COM17'  # Ganti sesuai port Anda (COM3, COM4, dll)
BAUD_RATE = 115200
DEVICE_ID = 1  # Device ID yang mau di-test (1-5)

# Protocol marker
SERIAL_DIST_MARKER = 0xBB

# ============================================
# FUNGSI HELPER
# ============================================

def create_packet(device_id, digital_value):
    """
    Buat paket 4-byte untuk kirim ke device
    Format: [0xBB][Device_ID][Byte_High][Byte_Low]
    
    Args:
        device_id: ID device (1-5)
        digital_value: Nilai digital 16-bit (0-65535)
    
    Returns:
        bytes: Paket 4-byte
    """
    byte_high = (digital_value >> 8) & 0xFF
    byte_low = digital_value & 0xFF
    
    packet = bytes([SERIAL_DIST_MARKER, device_id, byte_high, byte_low])
    return packet


def digital_to_degree(digital_value, device_id=1):
    """
    Convert nilai digital ke derajat sesuai encoding device
    
    Args:
        digital_value: Nilai digital 16-bit
        device_id: ID device (1-5)
    
    Returns:
        float: Nilai dalam derajat
    """
    if device_id == 5:
        # Device 5: Relative Course encoding
        signed_val = struct.unpack('h', struct.pack('H', digital_value))[0]
        degree = (signed_val / 10.0) - 179.9
    else:
        # Device 1-4: Standard encoding
        degree = digital_value / 10.0
    
    return degree


def degree_to_digital(degree, device_id=1):
    """
    Convert derajat ke nilai digital sesuai encoding device
    
    Args:
        degree: Nilai dalam derajat
        device_id: ID device (1-5)
    
    Returns:
        int: Nilai digital 16-bit
    """
    if device_id == 5:
        # Device 5: Relative Course encoding
        # Range: -179.9° to +179.9°
        digital = int((degree + 179.9) * 10)
        # Ensure in range
        digital = max(0, min(65535, digital))
    else:
        # Device 1-4: Standard encoding
        # Range: 0° to 360°
        digital = int(degree * 10)
        # Ensure in range
        digital = max(0, min(3600, digital))
    
    return digital


def test_single_angle(ser, device_id, degree):
    """
    Test kirim satu angle ke device
    
    Args:
        ser: Serial object
        device_id: ID device
        degree: Angle dalam derajat
    """
    # Convert degree to digital
    digital = degree_to_digital(degree, device_id)
    
    # Buat packet
    packet = create_packet(device_id, digital)
    
    # Kirim
    ser.write(packet)
    
    # Print info
    print(f"\n{'='*60}")
    print(f"📤 KIRIM ke Device #{device_id}")
    print(f"{'='*60}")
    print(f"Angle (degree)  : {degree:.2f}°")
    print(f"Digital Value   : {digital} (0x{digital:04X})")
    print(f"Packet (hex)    : {packet.hex().upper()}")
    print(f"  - Marker      : 0x{packet[0]:02X}")
    print(f"  - Device ID   : {packet[1]}")
    print(f"  - Byte High   : 0x{packet[2]:02X}")
    print(f"  - Byte Low    : 0x{packet[3]:02X}")
    
    # Tunggu response dari STM32 (jika ada)
    time.sleep(0.1)
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        print(f"\n📥 RESPONSE dari Device:")
        print(response.strip())
    
    # Info untuk motor synchro
    print(f"\n🔧 EXPECTED OUTPUT ke DSC Converter:")
    print(f"  - 16-bit Binary : {digital:016b}")
    print(f"  - Motor Angle   : {degree:.2f}°")
    print(f"{'='*60}\n")


def test_sweep(ser, device_id, start=0, end=360, step=45):
    """
    Test sweep angle dari start ke end
    
    Args:
        ser: Serial object
        device_id: ID device
        start: Start angle (degree)
        end: End angle (degree)
        step: Step size (degree)
    """
    print(f"\n🔄 SWEEP TEST: {start}° → {end}° (step: {step}°)")
    print(f"Device ID: {device_id}\n")
    
    angle = start
    while angle <= end:
        test_single_angle(ser, device_id, angle)
        time.sleep(1)  # Delay 1 detik antar angle
        angle += step


def interactive_mode(ser, device_id):
    """
    Mode interaktif untuk input manual
    
    Args:
        ser: Serial object
        device_id: ID device
    """
    print(f"\n🎮 INTERACTIVE MODE - Device #{device_id}")
    print("Ketik angle (0-360) atau 'q' untuk quit\n")
    
    while True:
        try:
            user_input = input("Angle (degree): ").strip()
            
            if user_input.lower() == 'q':
                print("Keluar dari interactive mode.")
                break
            
            degree = float(user_input)
            
            # Validasi range
            if device_id == 5:
                if degree < -179.9 or degree > 179.9:
                    print("❌ Error: Device #5 range: -179.9° to +179.9°")
                    continue
            else:
                if degree < 0 or degree > 360:
                    print("❌ Error: Range: 0° to 360°")
                    continue
            
            test_single_angle(ser, device_id, degree)
            
        except ValueError:
            print("❌ Error: Input harus angka!")
        except KeyboardInterrupt:
            print("\n\nKeluar dari interactive mode.")
            break


# ============================================
# MAIN PROGRAM
# ============================================

def main():
    print("="*60)
    print("  DSC_rome_device Test Script")
    print("  Motor Synchro Output Verification")
    print("="*60)
    
    # Buka serial port
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"\n✅ Serial port {SERIAL_PORT} opened successfully!")
        print(f"   Baud rate: {BAUD_RATE}")
        time.sleep(2)  # Tunggu STM32 ready
        
    except serial.SerialException as e:
        print(f"\n❌ Error opening serial port: {e}")
        print(f"\nPastikan:")
        print(f"  1. STM32 sudah terhubung")
        print(f"  2. Port {SERIAL_PORT} benar (cek Device Manager)")
        print(f"  3. Port tidak dipakai program lain")
        return
    
    try:
        # Menu
        while True:
            print("\n" + "="*60)
            print("MENU:")
            print("="*60)
            print("1. Test Single Angle")
            print("2. Test Sweep (0° - 360°)")
            print("3. Test Sweep Custom")
            print("4. Interactive Mode")
            print("5. Change Device ID")
            print("6. Exit")
            print("="*60)
            
            choice = input("\nPilih menu (1-6): ").strip()
            
            if choice == '1':
                degree = float(input("Masukkan angle (degree): "))
                test_single_angle(ser, DEVICE_ID, degree)
                
            elif choice == '2':
                test_sweep(ser, DEVICE_ID, start=0, end=360, step=45)
                
            elif choice == '3':
                start = float(input("Start angle: "))
                end = float(input("End angle: "))
                step = float(input("Step size: "))
                test_sweep(ser, DEVICE_ID, start, end, step)
                
            elif choice == '4':
                interactive_mode(ser, DEVICE_ID)
                
            elif choice == '5':
                new_id = int(input("Device ID baru (1-5): "))
                if 1 <= new_id <= 5:
                    globals()['DEVICE_ID'] = new_id
                    print(f"✅ Device ID changed to {new_id}")
                else:
                    print("❌ Error: Device ID harus 1-5")
                    
            elif choice == '6':
                print("\nKeluar dari program...")
                break
                
            else:
                print("❌ Pilihan tidak valid!")
    
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh user.")
    
    finally:
        ser.close()
        print("\n✅ Serial port closed.")
        print("="*60)


if __name__ == "__main__":
    main()
