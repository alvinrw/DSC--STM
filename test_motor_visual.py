#!/usr/bin/env python3
"""
Motor Synchro Visual Test - Real-time Circular Visualization
Auto-increment tiap 15 derajat dengan tampilan visual
"""

import serial
import time
import math
import os

# Konfigurasi
PORT = 'COM11'
BAUD = 115200
DEVICE_ID = 1
STEP_DEGREE = 15  # Increment tiap 15 derajat
DELAY_BETWEEN = 2  # Delay antar step (detik)

def create_packet(device_id, degree):
    """Create 4-byte packet for DSC_rome_device"""
    # Encoding: degree * 10 (e.g., 90° → 900)
    digital = int(degree * 10)
    byte_high = (digital >> 8) & 0xFF
    byte_low = digital & 0xFF
    
    # Packet: [0xBB][Device_ID][Byte_High][Byte_Low]
    return bytes([0xBB, device_id, byte_high, byte_low])

def draw_compass(degree):
    """Draw ASCII compass with needle pointing to degree"""
    size = 15  # Radius
    center_x = size
    center_y = size
    
    # Clear screen (Windows)
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\n" + "="*60)
    print(f"  MOTOR SYNCHRO VISUAL TEST - Device #{DEVICE_ID}")
    print("="*60)
    print(f"\n  Current Angle: {degree:3.0f}°")
    print(f"  Step: {STEP_DEGREE}° | Delay: {DELAY_BETWEEN}s")
    print("\n")
    
    # Create 2D grid
    grid = [[' ' for _ in range(size*2+1)] for _ in range(size*2+1)]
    
    # Draw circle
    for angle_deg in range(0, 360, 5):
        angle_rad = math.radians(angle_deg)
        x = int(center_x + size * math.cos(angle_rad))
        y = int(center_y + size * math.sin(angle_rad))
        if 0 <= x < size*2+1 and 0 <= y < size*2+1:
            grid[y][x] = '·'
    
    # Draw cardinal directions
    # North (0°)
    grid[0][center_x] = 'N'
    # East (90°)
    grid[center_y][size*2] = 'E'
    # South (180°)
    grid[size*2][center_x] = 'S'
    # West (270°)
    grid[center_y][0] = 'W'
    
    # Draw degree markers
    for deg in [0, 45, 90, 135, 180, 225, 270, 315]:
        angle_rad = math.radians(deg - 90)  # Adjust for screen coordinates
        x = int(center_x + (size-2) * math.cos(angle_rad))
        y = int(center_y + (size-2) * math.sin(angle_rad))
        if 0 <= x < size*2+1 and 0 <= y < size*2+1:
            if grid[y][x] not in ['N', 'E', 'S', 'W']:
                grid[y][x] = str(deg)[:1]
    
    # Draw needle (from center to edge)
    angle_rad = math.radians(degree - 90)  # Adjust for screen coordinates
    for r in range(1, size+1):
        x = int(center_x + r * math.cos(angle_rad))
        y = int(center_y + r * math.sin(angle_rad))
        if 0 <= x < size*2+1 and 0 <= y < size*2+1:
            if r == size:
                grid[y][x] = '►'  # Arrow head
            else:
                grid[y][x] = '─'
    
    # Draw center
    grid[center_y][center_x] = '●'
    
    # Print grid
    for row in grid:
        print("  " + ''.join(row))
    
    print("\n" + "-"*60)
    print(f"  Packet: {' '.join(f'{b:02X}' for b in create_packet(DEVICE_ID, degree))}")
    print("-"*60)

def main():
    """Main function"""
    try:
        # Connect
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"✓ Connected to {PORT}")
        time.sleep(2)
        
        # Clear buffer
        while ser.in_waiting > 0:
            ser.readline()
        
        print("\n🎯 Starting visual test...")
        print("Press Ctrl+C to stop\n")
        time.sleep(2)
        
        degree = 0
        
        while True:
            # Draw compass
            draw_compass(degree)
            
            # Send packet
            packet = create_packet(DEVICE_ID, degree)
            ser.write(packet)
            
            # Read response (optional)
            time.sleep(0.1)
            if ser.in_waiting > 0:
                response = ser.readline().decode().strip()
                print(f"  ← STM32: {response}")
            
            # Increment
            degree += STEP_DEGREE
            if degree > 360:
                degree = 0
                print("\n  🔄 Full rotation completed! Starting again...\n")
                time.sleep(1)
            
            # Wait before next
            time.sleep(DELAY_BETWEEN)
        
    except serial.SerialException as e:
        print(f"\n❌ Serial Error: {e}")
        print(f"Pastikan port {PORT} benar!")
    except KeyboardInterrupt:
        print("\n\n✓ Test stopped by user")
        if 'ser' in locals() and ser.is_open:
            ser.close()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
