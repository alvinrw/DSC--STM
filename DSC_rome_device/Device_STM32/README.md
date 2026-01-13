# Device STM32 Firmware

## Overview

Device STM32 receives individual data from Master STM32 via I2C, decodes based on DEVICE_ID, displays on OLED, and controls 16-bit GPIO output.

---

## Hardware Requirements

- **STM32F103** (or compatible) × 5 units
- **I2C1**: Connected to Master STM32
- **OLED Display**: SSD1306 (128x64, I2C)
- **GPIO**: 16-bit output for synchro control
- **LED**: Status indicator

---

## Functionality

### 1. Receive from Master
- Listens on I2C for 3-byte packets
- Validates start marker (`0xAA`)
- Extracts 16-bit data value

### 2. Decode Data
Applies encoding formula based on DEVICE_ID:

| Device ID | Function | Formula | Range |
|-----------|----------|---------|-------|
| 1 | Pitch | `value / 10` | 0-360° |
| 2 | Roll | `value / 10` | 0-360° |
| 3 | Bearing | `value / 10` | 0-360° |
| 4 | Compass | `value / 10` | 0-360° |
| 5 | Relative Course | `(value / 10) - 179.9` | -179.9° to +179.9° |

### 3. Display on OLED
Shows:
```
Device: #X
Digital: XXXXX
Syncro: XXX.XX
```

### 4. GPIO Output
Updates 16-bit GPIO with raw digital value for synchro control.

---

## Configuration

### Set Device ID

Edit `Inc/main.h`:
```c
#define DEVICE_ID 1  // Set to 1, 2, 3, 4, or 5
```

### Set I2C Address

Each device must have unique I2C address:
- Device #1: `0x10`
- Device #2: `0x11`
- Device #3: `0x12`
- Device #4: `0x13`
- Device #5: `0x14`

---

## Pin Configuration

| Pin | Function | Connection |
|-----|----------|------------|
| PB6 | I2C1 SCL | Master SCL |
| PB7 | I2C1 SDA | Master SDA |
| PB8 | I2C2 SCL | OLED SCL |
| PB9 | I2C2 SDA | OLED SDA |
| PA0-PA15 | GPIO | 16-bit synchro output |
| PC13 | LED | Status LED |

---

## Build & Flash

1. Open project in STM32CubeIDE
2. **Set DEVICE_ID** in `Inc/main.h` (1-5)
3. Build (Ctrl+B)
4. Flash to Device STM32
5. Repeat for all 5 devices with different DEVICE_IDs

---

## Status Indicators

- **LED ON**: Idle, waiting for data
- **LED Blink**: Data received and processed
- **LED OFF**: No power or error

---

## Communication Protocol

### Master → Device (I2C)
```
3 bytes:
AA [MSB] [LSB]
```

**Example (Pitch = 90°):**
```
Encoded: 90 × 10 = 900 = 0x0384
Packet: AA 03 84
```

---

## Troubleshooting

### OLED not updating
- Check I2C address matches DEVICE_ID
- Verify Master is sending data
- Check I2C pull-up resistors

### Wrong angle display
- Verify DEVICE_ID is set correctly
- Check encoding formula for device type
- Verify Master is sending correct data

### No I2C communication
- Check SCL/SDA connections
- Verify pull-up resistors (4.7kΩ)
- Check I2C address conflicts
