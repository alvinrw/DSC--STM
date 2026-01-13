import serial
import time
import struct

# ===== KONFIGURASI =====
PORT = 'COM11'     # Ganti dengan COM port USB-TTL kamu (Cek Device Manager)
BAUDRATE = 115200
# ========================

def create_packet(degrees):
    """
    Membuat paket 15 byte sesuai protokol:
    [0xA5, 0x99, 0, 0, 0, D1_H, D1_L, D2_H, D2_L, ..., D5_H, D5_L]
    """
    packet = bytearray(15)
    packet[0] = 0xA5  # Header 1
    packet[1] = 0x99  # Header 2
    # Byte 2-4: Padding/Reserved (0x00)
    
    # Isi Data Device 1-5 (Index 5-14)
    for i in range(5):
        val = degrees[i]
        # Pastikan value 16-bit
        val = max(0, min(65535, val))
        
        idx = 5 + (i * 2)
        packet[idx] = (val >> 8) & 0xFF     # MSB
        packet[idx+1] = val & 0xFF          # LSB
        
    return packet

def main():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"Terhubung ke {PORT} @ {BAUDRATE}")
    except Exception as e:
        print(f"Gagal buka port {PORT}: {e}")
        return

    print("\n=== FAKE RASPBERRY PI GENERATOR ===")
    print("Format input: 5 angka (derajat) dipisah spasi.")
    print("Contoh: 10 20 30 40 50")
    print("Ketik 'EXIT' untuk keluar.\n")

    try:
        while True:
            user_input = input("Masukkan 5 Data Derajat >> ")
            if user_input.upper() == 'EXIT':
                break
                
            try:
                # Parse input user
                values = [int(x) for x in user_input.split()]
                if len(values) != 5:
                    print(f"Error: Harus masukkan 5 angka! (Anda memasukkan {len(values)})")
                    continue
                
                # Konversi derajat (0-360) ke nilai raw 16-bit (0-65535) jika perlu
                # Asumsi: Input user adalah RAW VALUE yang mau dikirim ke OLED
                # Kalau inputnya derajat, mungkin perlu dikali faktor skala.
                # Kita kirim mentah saja sesuai input user.
                
                packet = create_packet(values)
                ser.write(packet)
                
                hex_str = ' '.join([f'{b:02X}' for b in packet])
                print(f"[SENT] {len(packet)} Bytes: {hex_str}")
                print("Cek apakah LED Master berkedip? Cek apakah Device berubah?\n")
                
            except ValueError:
                print("Error: Masukkan angka saja!")
                
    except KeyboardInterrupt:
        print("\nKeluar...")
    finally:
        ser.close()
        print("Port ditutup.")

if __name__ == "__main__":
    main()
