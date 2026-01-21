# Complete Guide: Discrete Data Parsing

## 📦 Packet Structure (15 bytes)

```
Byte 0    Byte 1    Byte 2     Byte 3     Byte 4     Byte 5-14
[0xA5]    [0x99]    [Disc A]   [Disc B]   [Disc C]   [Device Data 1-5]
Header1   Header2   8 bits     8 bits     8 bits     10 bytes (5 devices × 2 bytes)
```

---

## 🔍 Discrete A (Byte 2) - 8 Bits

### **Bit Mapping**:
| Bit | EADI Mode | EHSI Mode | RDU Mode |
|-----|-----------|-----------|----------|
| **0** | GS Valid | GS Valid | - |
| **1** | Gyro Monitor | TRUE/MAG Annun | - |
| **2** | F/D Validity Flag | FMS Decimal Display | - |
| **3** | ROT Valid Signal | Waypoint Alert | - |
| **4** | NVIS Sel | NVIS Sel | NVIS Sel |
| **5** | DH Input | - | - |
| **6** | - | - | Video Radar ON |
| **7** | - | - | - |

### **Code Example**:
```c
// Parse Discrete A
for(int i=0; i<8; i++){
    discreate_A[i] = (rx_buffer[2] >> i & 0x01);
}

// EADI Mode
uint8_t gs_valid = discreate_A[0];           // Bit 0
uint8_t gyro_monitor = discreate_A[1];       // Bit 1
uint8_t fd_validity_flag = discreate_A[2];   // Bit 2
uint8_t rot_valid_signal = discreate_A[3];   // Bit 3
uint8_t nvis_sel = discreate_A[4];           // Bit 4
uint8_t dh_input = discreate_A[5];           // Bit 5

// EHSI Mode
uint8_t true_mag_annun = discreate_A[1];     // Bit 1
uint8_t fms_decimal_display = discreate_A[2]; // Bit 2
uint8_t waypoint_alert = discreate_A[3];     // Bit 3

// RDU Mode
uint8_t video_radar_on = discreate_A[6];     // Bit 6
```

---

## 🔍 Discrete B (Byte 3) - 8 Bits

### **Bit Mapping**:
| Bit | EADI Mode | EHSI Mode | RDU Mode | Description |
|-----|-----------|-----------|----------|-------------|
| **0** | Run Mode [0] | Run Mode [0] | Run Mode [0] | LSB of Run Mode |
| **1** | Run Mode [1] | Run Mode [1] | Run Mode [1] | MSB of Run Mode |
| **2** | Nav Source [0] | Nav Source [0] | - | LSB of Nav Source |
| **3** | Nav Source [1] | Nav Source [1] | - | MSB of Nav Source |
| **4** | Auto Test | Auto Test | - | Auto Test Flag |
| **5** | LAT/BAR In View | Heading Monitor | - | Display specific |
| **6** | ILS Freq Tuned | ILS Freq Tuned | - | ILS Frequency |
| **7** | NAV Super Flag | NAV Valid Signal | - | Navigation status |

### **Run Mode (Bits 0-1)**:
```c
uint8_t run_mode = (discreate_B[1] << 1) | discreate_B[0];
// 0x00 = EADI
// 0x01 = EHSI
// 0x02 = RDU
```

### **Navigation Source (Bits 2-3)**:
```c
uint8_t nav_src = (discreate_B[3] << 1) | discreate_B[2];
// 0x00 = INS
// 0x01 = TAC
// 0x02 = VOR/ILS
```

### **Code Example**:
```c
// Parse Discrete B
for(int i=0; i<8; i++){
    discreate_B[i] = (rx_buffer[3] >> i & 0x01);
}

// Run Mode (ALL modes)
uint8_t run_mode = (discreate_B[1] << 1) | discreate_B[0];
const char *run_mode_str = NULL;
if(run_mode == 0x00) run_mode_str = "EADI";
else if(run_mode == 0x01) run_mode_str = "EHSI";
else if(run_mode == 0x02) run_mode_str = "RDU";

// Navigation Source (EADI & EHSI only)
uint8_t nav_src = (discreate_B[3] << 1) | discreate_B[2];
const char *navigation_source = NULL;
if(nav_src == 0x00) navigation_source = "INS";
else if(nav_src == 0x01) navigation_source = "TAC";
else if(nav_src == 0x02) navigation_source = "VOR/ILS";

// EADI Mode specific
uint8_t auto_test = discreate_B[4];          // Bit 4
uint8_t lat_bar_in_view = discreate_B[5];    // Bit 5
uint8_t ils_freq_tuned = discreate_B[6];     // Bit 6
uint8_t nav_super_flag = discreate_B[7];     // Bit 7

// EHSI Mode specific
uint8_t heading_monitor = discreate_B[5];    // Bit 5
uint8_t nav_valid_signal = discreate_B[7];   // Bit 7
```

---

## 🔍 Discrete C (Byte 4) - 8 Bits

### **Bit Mapping**:
| Bit | EADI Mode | EHSI Mode | RDU Mode | Description |
|-----|-----------|-----------|----------|-------------|
| **0** | Country Code [0] | Country Code [0] | Country Code [0] | LSB of Country |
| **1** | Country Code [1] | Country Code [1] | Country Code [1] | MSB of Country |
| **2** | Radio Altimeter Mon | - | - | Radio Alt Monitor |
| **3** | REV Mode Enable | Back Loc Sense | - | Mode specific |
| **4** | Inner Marker | - | - | Marker beacon |
| **5** | Outer Marker | VHF NAV Config | - | Config/Marker |
| **6** | Middle Marker | - | - | Marker beacon |
| **7** | - | - | - | Reserved |

### **Country Code (Bits 0-1)**:
```c
uint8_t country = (discreate_C[1] << 1) | discreate_C[0];
// 0x00 = TNI AU
// 0x01 = Bangladesh
```

### **Code Example**:
```c
// Parse Discrete C
for(int i=0; i<8; i++){
    discreate_C[i] = (rx_buffer[4] >> i & 0x01);
}

// Country Code (ALL modes)
uint8_t country = (discreate_C[1] << 1) | discreate_C[0];
const char *country_code = NULL;
if(country == 0x00) country_code = "TNI AU";
else if(country == 0x01) country_code = "Bangladesh";

// EADI Mode specific
uint8_t radio_altimeter_mon = discreate_C[2]; // Bit 2
uint8_t rev_mode_enable = discreate_C[3];     // Bit 3
uint8_t inner_marker = discreate_C[4];        // Bit 4
uint8_t outer_marker = discreate_C[5];        // Bit 5
uint8_t middle_marker = discreate_C[6];       // Bit 6

// EHSI Mode specific
uint8_t back_loc_sense = discreate_C[3];      // Bit 3
uint8_t vhf_nav_config = discreate_C[5];      // Bit 5
```

---

## 📊 Complete Bit Summary

### **EADI Mode** (21 active bits):
```
Discrete A: 6 bits (0-5)
Discrete B: 8 bits (0-7)
Discrete C: 7 bits (0-6)
Total: 21 bits
```

### **EHSI Mode** (14 active bits):
```
Discrete A: 4 bits (0-4)
Discrete B: 8 bits (0-7)
Discrete C: 2 bits (0-1, 3, 5)
Total: 14 bits
```

### **RDU Mode** (4 active bits):
```
Discrete A: 2 bits (4, 6)
Discrete B: 2 bits (0-1)
Discrete C: 2 bits (0-1)
Total: 4 bits (minimal!)
```

---

## 💡 Usage Example

```c
// Detect mode first
uint8_t run_mode = (discreate_B[1] << 1) | discreate_B[0];

if(run_mode == 0x00){  // EADI Mode
    // Parse EADI-specific bits
    if(inner_marker || middle_marker || outer_marker){
        // Approaching runway
    }
    if(gyro_monitor == 0){
        // Gyro failure warning
    }
}
else if(run_mode == 0x01){  // EHSI Mode
    // Parse EHSI-specific bits
    if(waypoint_alert){
        // Waypoint approaching
    }
    if(heading_monitor == 0){
        // Heading system failure
    }
}
else if(run_mode == 0x02){  // RDU Mode
    // Parse RDU-specific bits
    if(video_radar_on){
        // Radar display active
    }
}
```

---

## 🎯 Key Points

1. **Discrete A, B, C** = 3 bytes (24 bits total)
2. **Bit meaning changes** per mode (EADI/EHSI/RDU)
3. **Common bits** across all modes:
   - Run Mode (B0-B1)
   - Country Code (C0-C1)
   - NVIS Sel (A4)
4. **Mode-specific bits** harus di-parse sesuai run mode
5. **Total active bits**: EADI=21, EHSI=14, RDU=4

**Semua discrete data sekarang ter-dokumentasi lengkap!** 🎉
