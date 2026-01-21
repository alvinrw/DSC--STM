# Test Script untuk DSC_rome_device

## 📋 Deskripsi

Script Python untuk testing komunikasi dengan DSC_rome_device dan verifikasi output ke motor synchro melalui DSC converter.

## 🔧 Cara Pakai

### 1. Install Dependencies

```bash
pip install pyserial
```

### 2. Konfigurasi

Edit file `test_device_motor.py`:

```python
SERIAL_PORT = 'COM3'  # Ganti sesuai port Anda
BAUD_RATE = 115200
DEVICE_ID = 1         # Device ID yang mau di-test (1-5)
```

**Cara cek port:**
- Windows: Buka Device Manager → Ports (COM & LPT)
- Linux/Mac: `ls /dev/tty*`

### 3. Jalankan Script

```bash
python test_device_motor.py
```

## 📖 Menu

### 1. Test Single Angle
Kirim satu angle tertentu ke device.

**Contoh:**
```
Masukkan angle: 45
```

**Output:**
```
📤 KIRIM ke Device #1
Angle (degree)  : 45.00°
Digital Value   : 450 (0x01C2)
Packet (hex)    : BB0101C2

🔧 EXPECTED OUTPUT ke DSC Converter:
  - 16-bit Binary : 0000000111000010
  - Motor Angle   : 45.00°
```

### 2. Test Sweep (0° - 360°)
Auto sweep dari 0° sampai 360° dengan step 45°.

**Output motor:** Berputar dari 0° → 45° → 90° → ... → 360°

### 3. Test Sweep Custom
Sweep dengan range dan step custom.

**Contoh:**
```
Start angle: 0
End angle: 180
Step size: 30
```

### 4. Interactive Mode
Input angle manual secara interaktif.

**Contoh:**
```
Angle (degree): 90
Angle (degree): 180
Angle (degree): 270
Angle (degree): q  (untuk quit)
```

### 5. Change Device ID
Ganti device ID yang mau di-test (1-5).

## 🎯 Cara Verifikasi

### Cek di OLED STM32:
```
Device: #1
Digital: 450
Syncro: 45.00
```

### Cek Motor Synchro:
1. Motor harus **berputar** sesuai angle yang dikirim
2. Angle 0° = posisi referensi
3. Angle 180° = posisi berlawanan
4. Angle 360° = kembali ke posisi 0°

### Cek dengan Multimeter (jika ada DSC):
- Ukur output S1, S2, S3 dari DSC converter
- Harus ada tegangan AC (11.8V atau 90V tergantung DSC)
- S1, S2, S3 harus berbeda phase (120°)

## 📊 Format Packet

```
[0xBB] [Device_ID] [Byte_High] [Byte_Low]
  ↑         ↑           ↑           ↑
Marker    1-5      MSB 8-bit   LSB 8-bit
```

**Contoh untuk 45°:**
- Degree: 45.00°
- Digital: 45.00 × 10 = 450
- Hex: 0x01C2
- Packet: `BB 01 01 C2`

## 🔍 Troubleshooting

### Error: Serial port tidak bisa dibuka
```
❌ Error opening serial port: [WinError 5] Access is denied
```

**Solusi:**
1. Tutup program lain yang pakai port (Arduino IDE, PuTTY, dll)
2. Cek port sudah benar di Device Manager
3. Coba unplug-plug USB

### Motor tidak berputar

**Cek:**
1. ✅ STM32 dapat data? (cek OLED)
2. ✅ GPIO output ke DSC sudah benar? (16 pin + EN)
3. ✅ DSC dapat power? (±15V, +5V)
4. ✅ DSC reference input ada? (26V/115V AC)
5. ✅ Motor synchro dapat power?

### Angle tidak akurat

**Cek:**
1. Encoding device benar? (Device 1-4 vs Device 5)
2. DSC resolution setting (14-bit vs 16-bit)
3. Kalibrasi motor synchro

## 📝 Device Encoding

### Device 1-4 (Standard):
- Range: 0° - 360°
- Encoding: `digital = degree × 10`
- Max value: 3600

### Device 5 (Relative Course):
- Range: -179.9° to +179.9°
- Encoding: `digital = (degree + 179.9) × 10`
- Max value: 3599

## 🎓 Contoh Penggunaan

### Test Basic:
```bash
python test_device_motor.py
# Pilih menu 1
# Input: 90
# Motor harus putar ke 90°
```

### Test Full Rotation:
```bash
python test_device_motor.py
# Pilih menu 2
# Motor akan sweep 0° → 360°
```

### Test Precision:
```bash
python test_device_motor.py
# Pilih menu 4 (Interactive)
# Test angle: 0, 45, 90, 135, 180, 225, 270, 315, 360
# Cek akurasi motor di setiap posisi
```
