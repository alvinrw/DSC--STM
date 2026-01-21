#!/usr/bin/env python3
"""
Motor Synchro Accuracy Test & Visualization
Untuk test akurasi motor synchro dengan mapping visual
"""

import serial
import time
from datetime import datetime

# Konfigurasi
PORT = 'COM11'  # Sesuaikan dengan port Anda
BAUD = 115200
DEVICE_ID = 1

# Test angles (derajat)
TEST_ANGLES = [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330, 360]

def create_packet(device_id, degree):
    """Create 4-byte packet for DSC_rome_device"""
    digital = int(degree * 10)
    byte_high = (digital >> 8) & 0xFF
    byte_low = digital & 0xFF
    return bytes([0xBB, device_id, byte_high, byte_low])

def create_broadcast(device_id, degree):
    """Create 15-byte broadcast for Kode_lama"""
    packet = [0xA5, 0x99, 0x00, 0x00, 0x00]
    
    for dev in range(1, 6):
        if dev == device_id:
            digital = int(degree * 10)
            byte_high = (digital >> 8) & 0xFF
            byte_low = digital & 0xFF
            packet.extend([byte_high, byte_low])
        else:
            packet.extend([0x00, 0x00])
    
    return bytes(packet)

def print_header():
    """Print test header"""
    print("\n" + "="*80)
    print("  MOTOR SYNCHRO ACCURACY TEST")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*80)
    print(f"\n  Port: {PORT} | Baud: {BAUD} | Device: #{DEVICE_ID}")
    print(f"  Test Points: {len(TEST_ANGLES)} angles")
    print("\n" + "-"*80)
    print(f"{'No':<4} {'Sent (°)':<10} {'Motor (°)':<12} {'Error (°)':<12} {'Status':<10}")
    print("-"*80)

def print_result(idx, sent, actual, error):
    """Print single test result"""
    if abs(error) <= 2:
        status = "✓ OK"
    elif abs(error) <= 5:
        status = "⚠ WARN"
    else:
        status = "✗ FAIL"
    
    print(f"{idx:<4} {sent:<10.1f} {actual:<12.1f} {error:+12.1f} {status:<10}")

def print_summary(results):
    """Print test summary with statistics"""
    print("-"*80)
    print("\n📊 TEST SUMMARY:")
    print("-"*80)
    
    errors = [abs(r['error']) for r in results]
    avg_error = sum(errors) / len(errors)
    max_error = max(errors)
    min_error = min(errors)
    
    ok_count = sum(1 for e in errors if e <= 2)
    warn_count = sum(1 for e in errors if 2 < e <= 5)
    fail_count = sum(1 for e in errors if e > 5)
    
    print(f"  Total Tests    : {len(results)}")
    print(f"  ✓ OK (≤2°)     : {ok_count} ({ok_count/len(results)*100:.1f}%)")
    print(f"  ⚠ Warning (≤5°): {warn_count} ({warn_count/len(results)*100:.1f}%)")
    print(f"  ✗ Failed (>5°) : {fail_count} ({fail_count/len(results)*100:.1f}%)")
    print()
    print(f"  Average Error  : {avg_error:.2f}°")
    print(f"  Max Error      : {max_error:.2f}°")
    print(f"  Min Error      : {min_error:.2f}°")
    
    # Simple ASCII graph
    print("\n📈 ERROR DISTRIBUTION:")
    print("-"*80)
    for i, result in enumerate(results):
        angle = result['sent']
        error = result['error']
        bar_len = int(abs(error) * 2)  # Scale for visibility
        bar = "█" * min(bar_len, 40)
        sign = "+" if error > 0 else "-"
        print(f"  {angle:3.0f}° {sign}{bar} {abs(error):.1f}°")
    
    print("="*80)

def main():
    """Main test function"""
    # Pilih mode
    print("\n🔧 SELECT FIRMWARE MODE:")
    print("  1. DSC_rome_device (4-byte individual)")
    print("  2. Kode_lama (15-byte broadcast)")
    
    mode = input("\nEnter mode (1 or 2): ").strip()
    
    if mode == "1":
        create_packet_func = create_packet
        mode_name = "DSC_rome_device"
    elif mode == "2":
        create_packet_func = create_broadcast
        mode_name = "Kode_lama"
    else:
        print("❌ Invalid mode!")
        return
    
    print(f"\n✓ Selected: {mode_name}")
    
    try:
        # Connect
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"✓ Connected to {PORT}")
        time.sleep(2)
        
        # Clear buffer
        while ser.in_waiting > 0:
            ser.readline()
        
        print_header()
        
        results = []
        
        # Test each angle
        for idx, angle in enumerate(TEST_ANGLES, 1):
            # Send packet
            packet = create_packet_func(DEVICE_ID, angle)
            ser.write(packet)
            time.sleep(0.5)  # Wait for motor to settle
            
            # For now, assume motor follows command
            # TODO: Add actual motor position reading if available
            print("\n📍 MANUAL INPUT REQUIRED:")
            print(f"   Sent: {angle}°")
            actual_str = input(f"   Enter actual motor position (°): ").strip()
            
            try:
                actual = float(actual_str)
                error = actual - angle
                
                results.append({
                    'sent': angle,
                    'actual': actual,
                    'error': error
                })
                
                print_result(idx, angle, actual, error)
                
            except ValueError:
                print("   ⚠ Invalid input, skipping...")
                continue
        
        # Print summary
        if results:
            print_summary(results)
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"motor_test_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.write(f"Motor Synchro Accuracy Test\n")
                f.write(f"Date: {datetime.now()}\n")
                f.write(f"Mode: {mode_name}\n")
                f.write(f"Device: #{DEVICE_ID}\n\n")
                f.write(f"{'Sent (°)':<10} {'Actual (°)':<12} {'Error (°)':<12}\n")
                f.write("-"*40 + "\n")
                
                for r in results:
                    f.write(f"{r['sent']:<10.1f} {r['actual']:<12.1f} {r['error']:+12.1f}\n")
            
            print(f"\n💾 Results saved to: {filename}")
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"❌ Serial Error: {e}")
    except KeyboardInterrupt:
        print("\n\n✓ Test stopped by user")
        if 'ser' in locals() and ser.is_open:
            ser.close()
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
