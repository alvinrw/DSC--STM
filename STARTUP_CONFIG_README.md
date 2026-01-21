# Konfigurasi Startup DSC_rome_device

## 📋 Settingan yang Bisa Diganti

Di bagian **ATAS** file `main.c` (sekitar line 27-32), ada settingan yang mudah diganti:

```c
// ============================================
// KONFIGURASI STARTUP - MUDAH DIGANTI!
// ============================================
#define STARTUP_INIT_ANGLE      0.0f    // Angle awal saat startup (dalam derajat)
#define STARTUP_DELAY_MS        300     // Delay setelah init angle (dalam ms)
#define OLED_UPDATE_DELAY_MS    50      // Delay antar update OLED (dalam ms)
// ============================================
```

---

## 🎯 Cara Ganti Settingan

### 1. Ganti Angle Awal

**Contoh: Mau startup di 45°**
```c
#define STARTUP_INIT_ANGLE      45.0f   // Startup di 45 derajat
```

**Contoh: Mau startup di 180°**
```c
#define STARTUP_INIT_ANGLE      180.0f  // Startup di 180 derajat
```

**Range:**
- Device 1-4: `0.0f` sampai `360.0f`
- Device 5: `-179.9f` sampai `179.9f`

---

### 2. Ganti Delay Startup

**Contoh: Delay 500ms**
```c
#define STARTUP_DELAY_MS        500     // Delay 500 milidetik
```

**Contoh: Delay 1 detik**
```c
#define STARTUP_DELAY_MS        1000    // Delay 1 detik
```

**Fungsi:** Waktu tunggu setelah init angle sebelum mulai terima data

---

### 3. Ganti Delay OLED Update

**Contoh: Update lebih cepat**
```c
#define OLED_UPDATE_DELAY_MS    20      // Update lebih cepat
```

**Contoh: Update lebih lambat**
```c
#define OLED_UPDATE_DELAY_MS    100     // Update lebih lambat
```

**Fungsi:** Delay antar update OLED saat startup (untuk stabilitas)

---

## 🔄 Urutan Startup

Saat STM32 boot, ini yang terjadi:

```
1. Init OLED display
   ↓
2. Tampilkan "Device: #X"
   ↓
3. Set angle awal = STARTUP_INIT_ANGLE (default: 0°)
   ↓
4. Output ke GPIO → DSC Converter → Motor Synchro
   ↓
5. Update OLED dengan angle awal
   ↓
6. Delay STARTUP_DELAY_MS (default: 300ms)
   ↓
7. Kirim "Device #X Ready" via UART
   ↓
8. Mulai terima data dari Master
```

---

## 💡 Contoh Penggunaan

### Contoh 1: Startup di 0° dengan delay 300ms (DEFAULT)
```c
#define STARTUP_INIT_ANGLE      0.0f
#define STARTUP_DELAY_MS        300
```

**Hasil:**
- Motor synchro mulai di posisi 0°
- Tunggu 300ms
- Siap terima data

---

### Contoh 2: Startup di 90° dengan delay 500ms
```c
#define STARTUP_INIT_ANGLE      90.0f
#define STARTUP_DELAY_MS        500
```

**Hasil:**
- Motor synchro mulai di posisi 90°
- Tunggu 500ms
- Siap terima data

---

### Contoh 3: Startup di 180° tanpa delay
```c
#define STARTUP_INIT_ANGLE      180.0f
#define STARTUP_DELAY_MS        0
```

**Hasil:**
- Motor synchro mulai di posisi 180°
- Langsung siap terima data (no delay)

---

## 🔧 Cara Compile & Upload

1. **Edit** `main.c` → Ganti nilai di bagian atas
2. **Save** file
3. **Build** project di STM32CubeIDE
4. **Upload** ke STM32
5. **Test** dengan script Python:
   ```bash
   python test_device_motor.py
   ```

---

## 📊 Output UART Saat Startup

Setelah startup, STM32 akan kirim pesan via UART:

```
Device #1 Ready (Init: 0.00 deg)
```

Atau kalau Anda ganti jadi 45°:

```
Device #1 Ready (Init: 45.00 deg)
```

---

## ⚠️ Catatan Penting

1. **Angle harus sesuai range device:**
   - Device 1-4: 0° - 360°
   - Device 5: -179.9° - 179.9°

2. **Delay terlalu kecil** bisa bikin OLED tidak stabil

3. **Delay terlalu besar** bikin startup lama

4. **Rekomendasi:**
   - STARTUP_DELAY_MS: 200-500ms
   - OLED_UPDATE_DELAY_MS: 20-100ms
