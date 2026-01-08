import serial
import time

PORT = 'COM11'
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to {PORT}")
    time.sleep(2)
    
    # Baca pesan awal dari STM32
    print("\n=== Reading initial message ===")
    time.sleep(0.5)
    while ser.in_waiting > 0:
        msg = ser.readline().decode().strip()
        print(f"← {msg}")
    
    # Test 1: Kirim device command
    print("\n=== Test 1: Device-specific command ===")
    print("Sending: #1")
    ser.write(b"#1\n")
    time.sleep(0.2)
    
    print("Sending: 0x80 0x00")
    ser.write(b"0x80 0x00\n")
    time.sleep(0.5)
    
    # Baca response
    print("Response:")
    while ser.in_waiting > 0:
        msg = ser.readline().decode().strip()
        print(f"← {msg}")
    
    # Test 2: Kirim broadcast (15 bytes dengan header)
    print("\n=== Test 2: Broadcast ===")
    print("Sending: 0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF")
    ser.write(b"0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF\n")
    time.sleep(0.5)
    
    # Baca response
    print("Response:")
    while ser.in_waiting > 0:
        msg = ser.readline().decode().strip()
        print(f"← {msg}")
    
    ser.close()
    print("\n✓ Test complete")
    
except Exception as e:
    print(f"Error: {e}")
