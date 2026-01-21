# Complete Discrete Data Parsing - EADI Mode

## ✅ Semua Discrete Bits Sudah Di-Parse!

### **Discrete A** (Byte 2) - 6 bits aktif
```c
uint8_t gs_valid = discreate_A[0];           // GS Valid
uint8_t gyro_monitor = discreate_A[1];       // Gyro Monitor
uint8_t fd_validity_flag = discreate_A[2];   // F/D Validity Flag
uint8_t rot_valid_signal = discreate_A[3];   // ROT Valid Signal
uint8_t nvis_sel = discreate_A[4];           // NVIS Sel
uint8_t dh_input = discreate_A[5];           // DH Input
```

### **Discrete B** (Byte 3) - 8 bits aktif
```c
// Bit 0-1: EFD-5.5 Run Mode
uint8_t run_mode = (discreate_B[1] << 1) | discreate_B[0];
const char *run_mode_str = NULL;
if(run_mode == 0x00) run_mode_str = "EADI";
else if(run_mode == 0x01) run_mode_str = "EHSI";
else if(run_mode == 0x02) run_mode_str = "RDU";

// Bit 2-3: Navigation Source
uint8_t nav_src = (discreate_B[3] << 1) | discreate_B[2];
if(nav_src == 0x00) navigation_source = "INS";
else if(nav_src == 0x01) navigation_source = "TAC";
else if(nav_src == 0x02) navigation_source = "VOR/ILS";

uint8_t auto_test = discreate_B[4];          // Auto Test
uint8_t lat_bar_in_view = discreate_B[5];    // LAT/BAR In View
uint8_t ils_freq_tuned = discreate_B[6];     // ILS Freq Tuned
uint8_t nav_super_flag = discreate_B[7];     // NAV Super Flag
```

### **Discrete C** (Byte 4) - 7 bits aktif
```c
// Bit 0-1: Country Code
uint8_t country = (discreate_C[1] << 1) | discreate_C[0];
if(country == 0x00) country_code = "TNI AU";
else if(country == 0x01) country_code = "Bangladesh";

uint8_t radio_altimeter_mon = discreate_C[2]; // Radio Altimeter Mon
uint8_t rev_mode_enable = discreate_C[3];     // REV Mode Enable
uint8_t inner_marker = discreate_C[4];        // Inner Marker
uint8_t outer_marker = discreate_C[5];        // Outer Marker
uint8_t middle_marker = discreate_C[6];       // Middle Marker
```

---

## 📊 Discrete Bits Summary

| Discrete | Total Bits | Active Bits | Purpose |
|----------|------------|-------------|---------|
| **A** | 8 | 6 | System validity flags |
| **B** | 8 | 8 | Run mode, navigation, display |
| **C** | 8 | 7 | Country, markers, altimeter |
| **TOTAL** | 24 | 21 | Complete EADI discrete data |

---

## 💡 Cara Pakai

Semua variabel discrete sudah tersedia di dalam scope setelah parsing. Contoh penggunaan:

### **Example 1: Logging**
```c
if(run_mode_str != NULL){
    char log_msg[100];
    sprintf(log_msg, "Mode: %s, Nav: %s, Country: %s\r\n", 
            run_mode_str, navigation_source, country_code);
    HAL_UART_Transmit(&huart1, (uint8_t*)log_msg, strlen(log_msg), 100);
}
```

### **Example 2: Conditional Logic**
```c
if(auto_test == 1){
    // System in auto test mode
    // Skip normal processing
}

if(inner_marker == 1 || middle_marker == 1 || outer_marker == 1){
    // Approaching runway - activate marker logic
}
```

### **Example 3: Display**
```c
if(run_mode == 0x00){  // EADI mode
    // Display pitch and roll data
} else if(run_mode == 0x01){  // EHSI mode
    // Display heading and course data
}
```

---

## 🎯 Variables Available

### **String Variables**:
- `run_mode_str` - "EADI" / "EHSI" / "RDU"
- `navigation_source` - "INS" / "TAC" / "VOR/ILS"
- `country_code` - "TNI AU" / "Bangladesh"

### **Flag Variables** (uint8_t, 0 or 1):
- `gs_valid`, `gyro_monitor`, `fd_validity_flag`
- `rot_valid_signal`, `nvis_sel`, `dh_input`
- `auto_test`, `lat_bar_in_view`, `ils_freq_tuned`, `nav_super_flag`
- `radio_altimeter_mon`, `rev_mode_enable`
- `inner_marker`, `outer_marker`, `middle_marker`

---

## ⚠️ Note

Discrete bits **BERBEDA** per mode! Berikut mapping lengkap:

---

## 📋 EHSI Mode Discrete Bits

### **Discrete A** (Byte 2) - EHSI Mode
```c
uint8_t gs_valid = discreate_A[0];           // GS Valid (sama)
uint8_t true_mag_annun = discreate_A[1];     // TRUE/MAG Annun (beda!)
uint8_t fms_decimal_display = discreate_A[2]; // FMS Decimal Display (beda!)
uint8_t waypoint_alert = discreate_A[3];     // Waypoint Alert (beda!)
uint8_t nvis_sel = discreate_A[4];           // NVIS Sel (sama)
// Bit 5-7: Reserved
```

### **Discrete B** (Byte 3) - EHSI Mode
```c
// Bit 0-1: EFD-5.5 Run Mode (SAMA)
uint8_t run_mode = (discreate_B[1] << 1) | discreate_B[0];

// Bit 2-3: Navigation Source (SAMA)
uint8_t nav_src = (discreate_B[3] << 1) | discreate_B[2];

uint8_t auto_test = discreate_B[4];          // Auto Test (sama)
uint8_t heading_monitor = discreate_B[5];    // Heading Monitor (beda!)
uint8_t ils_freq_tuned = discreate_B[6];     // ILS Freq Tuned (sama)
uint8_t nav_valid_signal = discreate_B[7];   // NAV Valid Signal (beda!)
```

### **Discrete C** (Byte 4) - EHSI Mode
```c
// Bit 0-1: Country Code (SAMA)
uint8_t country = (discreate_C[1] << 1) | discreate_C[0];

// Bit 2: Reserved (beda!)
uint8_t back_loc_sense = discreate_C[3];     // Back Loc Sense (beda!)
// Bit 4: Reserved (beda!)
uint8_t vhf_nav_config = discreate_C[5];     // VHF NAV Config (beda!)
// Bit 6-7: Reserved
```

---

## 🔄 Perbedaan EADI vs EHSI

| Bit | EADI Mode | EHSI Mode |
|-----|-----------|-----------|
| **A[1]** | Gyro Monitor | TRUE/MAG Annun |
| **A[2]** | F/D Validity Flag | FMS Decimal Display |
| **A[3]** | ROT Valid Signal | Waypoint Alert |
| **A[5]** | DH Input | (Reserved) |
| **B[5]** | LAT/BAR In View | Heading Monitor |
| **B[7]** | NAV Super Flag | NAV Valid Signal |
| **C[2]** | Radio Altimeter Mon | (Reserved) |
| **C[3]** | REV Mode Enable | Back Loc Sense |
| **C[4]** | Inner Marker | (Reserved) |
| **C[5]** | Outer Marker | VHF NAV Config |
| **C[6]** | Middle Marker | (Reserved) |

---

## 💡 Implementasi di Code

Karena discrete bits **berbeda per mode**, kamu bisa pakai conditional parsing:

```c
// Parse discrete arrays dulu
for(int i=0; i<8; i++){
  discreate_A[i] = (rx_buffer[2] >> i & 0x01);
  discreate_B[i] = (rx_buffer[3] >> i & 0x01);
  discreate_C[i] = (rx_buffer[4] >> i & 0x01);
}

// Detect run mode
uint8_t run_mode = (discreate_B[1] << 1) | discreate_B[0];

if(run_mode == 0x00){  // EADI Mode
  uint8_t gyro_monitor = discreate_A[1];
  uint8_t fd_validity_flag = discreate_A[2];
  uint8_t rot_valid_signal = discreate_A[3];
  uint8_t dh_input = discreate_A[5];
  // ... EADI specific bits
}
else if(run_mode == 0x01){  // EHSI Mode
  uint8_t true_mag_annun = discreate_A[1];
  uint8_t fms_decimal_display = discreate_A[2];
  uint8_t waypoint_alert = discreate_A[3];
  // ... EHSI specific bits
}
```

---

Sekarang **SEMUA DISCRETE BITS SUDAH LENGKAP** untuk EADI dan EHSI mode! 🎉

---

## 📋 RDU Mode Discrete Bits

### **Discrete A** (Byte 2) - RDU Mode
```c
// Hampir semua kosong!
uint8_t nvis_sel = discreate_A[4];           // NVIS Sel (sama)
uint8_t video_radar_on = discreate_A[6];     // Video Radar ON (unik!)
// Bit 0-3, 5, 7: Reserved
```

### **Discrete B** (Byte 3) - RDU Mode
```c
// Bit 0-1: EFD-5.5 Run Mode (SAMA)
uint8_t run_mode = (discreate_B[1] << 1) | discreate_B[0];
// Bit 2-7: Reserved (semua kosong!)
```

### **Discrete C** (Byte 4) - RDU Mode
```c
// Bit 0-1: Country Code (SAMA)
uint8_t country = (discreate_C[1] << 1) | discreate_C[0];
// Bit 2-7: Reserved (semua kosong!)
```

**RDU Mode = MINIMAL DISCRETE DATA!** Hanya 4 bits aktif total.

---

## 🔄 Comparison: EADI vs EHSI vs RDU

| Bit | EADI Mode | EHSI Mode | RDU Mode |
|-----|-----------|-----------|----------|
| **A[0]** | GS Valid | GS Valid | - |
| **A[1]** | Gyro Monitor | TRUE/MAG Annun | - |
| **A[2]** | F/D Validity Flag | FMS Decimal Display | - |
| **A[3]** | ROT Valid Signal | Waypoint Alert | - |
| **A[4]** | NVIS Sel | NVIS Sel | **NVIS Sel** |
| **A[5]** | DH Input | - | - |
| **A[6]** | - | - | **Video Radar ON** |
| **A[7]** | - | - | - |
| **B[0-1]** | **Run Mode** | **Run Mode** | **Run Mode** |
| **B[2-3]** | **Nav Source** | **Nav Source** | - |
| **B[4]** | Auto Test | Auto Test | - |
| **B[5]** | LAT/BAR In View | Heading Monitor | - |
| **B[6]** | ILS Freq Tuned | ILS Freq Tuned | - |
| **B[7]** | NAV Super Flag | NAV Valid Signal | - |
| **C[0-1]** | **Country Code** | **Country Code** | **Country Code** |
| **C[2]** | Radio Alt Mon | - | - |
| **C[3]** | REV Mode Enable | Back Loc Sense | - |
| **C[4]** | Inner Marker | - | - |
| **C[5]** | Outer Marker | VHF NAV Config | - |
| **C[6]** | Middle Marker | - | - |
| **C[7]** | - | - | - |

---

## 💡 Implementasi Lengkap (3 Modes)

```c
// Parse discrete arrays
for(int i=0; i<8; i++){
  discreate_A[i] = (rx_buffer[2] >> i & 0x01);
  discreate_B[i] = (rx_buffer[3] >> i & 0x01);
  discreate_C[i] = (rx_buffer[4] >> i & 0x01);
}

// Detect run mode
uint8_t run_mode = (discreate_B[1] << 1) | discreate_B[0];

// Common bits (semua mode)
uint8_t country = (discreate_C[1] << 1) | discreate_C[0];
if(country == 0x00) country_code = "TNI AU";
else if(country == 0x01) country_code = "Bangladesh";

uint8_t nvis_sel = discreate_A[4];  // Ada di semua mode

// Mode-specific parsing
if(run_mode == 0x00){  // EADI Mode
  uint8_t gyro_monitor = discreate_A[1];
  uint8_t fd_validity_flag = discreate_A[2];
  uint8_t inner_marker = discreate_C[4];
  // ... 21 bits total
}
else if(run_mode == 0x01){  // EHSI Mode
  uint8_t true_mag_annun = discreate_A[1];
  uint8_t waypoint_alert = discreate_A[3];
  uint8_t heading_monitor = discreate_B[5];
  // ... 14 bits total
}
else if(run_mode == 0x02){  // RDU Mode
  uint8_t video_radar_on = discreate_A[6];
  // ... 4 bits total (minimal!)
}
```

---

## ✨ COMPLETE! Semua 3 Modes Sudah Lengkap!

- ✅ **EADI**: 21 discrete bits
- ✅ **EHSI**: 14 discrete bits  
- ✅ **RDU**: 4 discrete bits

**Total dokumentasi lengkap untuk semua mode!** 🎉

