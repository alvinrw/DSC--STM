# DSC-ROME Test Bench

Digital Synchro Converter - ROME (Resolver Output Motor Emulator) Test Bench for protocol development and validation.

## Overview

This project implements a 15-byte broadcast protocol for controlling up to 5 synchro motor devices simultaneously via UART communication. The system is designed as a test bench to validate the communication protocol before deployment on Raspberry Pi 3B.

## System Architecture

```
Raspberry Pi 3B (Future)
      |
   [UART TX] ──────┬──────┬──────┬──────┬──────┐
                   |      |      |      |      |
                STM32  STM32  STM32  STM32  STM32
                Dev#1  Dev#2  Dev#3  Dev#4  Dev#5
                   |      |      |      |      |
              Synchro Motor (16-bit Digital Output)
```

### Current Test Setup
- **Controller:** PC (via USB-UART adapter)
- **Target:** STM32 microcontrollers (1-5 devices)
- **Communication:** UART @ 115200 baud, shared bus
- **Protocol:** 15-byte broadcast with header validation

## Protocol Specification

### 15-Byte Broadcast Format

| Byte Position | Purpose | Example | Description |
|---------------|---------|---------|-------------|
| 1-2 | Header | `0xA5 0x99` | Protocol validation (mandatory) |
| 3-5 | Reserved | `0x00 0x00 0x00` | Reserved for future use |
| 6-7 | Device #1 Data | `0x00 0x00` | 16-bit position (0-65535) |
| 8-9 | Device #2 Data | `0x40 0x00` | 16-bit position (0-65535) |
| 10-11 | Device #3 Data | `0x80 0x00` | 16-bit position (0-65535) |
| 12-13 | Device #4 Data | `0xC0 0x00` | 16-bit position (0-65535) |
| 14-15 | Device #5 Data | `0xFF 0xFF` | 16-bit position (0-65535) |

### Position Encoding

The 16-bit digital value represents angular position:
- **Formula:** `Digital = (Degree / 360) × 65535`
- **Range:** 0x0000 (0°) to 0xFFFF (360°)
- **Resolution:** 0.0055° per LSB

**Example Mappings:**

| Degree | HEX Value | Decimal |
|--------|-----------|---------|
| 0° | 0x0000 | 0 |
| 90° | 0x4000 | 16384 |
| 180° | 0x8000 | 32768 |
| 270° | 0xC000 | 49152 |
| 360° | 0xFFFF | 65535 |

### Packet Validation

STM32 firmware validates incoming packets:
1. **Byte count:** Must be exactly 15 bytes
2. **Header:** First two bytes must be `0xA5 0x99`
3. **Invalid packets:** Silently discarded (no error response)

## Hardware Components

### STM32 Firmware
- **MCU:** STM32 series (tested on STM32F103)
- **Display:** SSD1306 OLED (128x64, I2C)
- **GPIO Output:** 16 pins (B1-B16) for digital synchro output
- **UART:** 115200 baud, 8N1
- **LED:** Status indicator (ON = idle, blink = data received)

### Device Configuration
Each STM32 device has a unique `DEVICE_ID` (1-5) configured in firmware:
```c
// In main.h
#define DEVICE_ID 1  // Change to 1, 2, 3, 4, or 5
```

## UART Test Scripts

All Python test scripts are located in the `UART/` directory.

### broadcast_controller.py
Interactive broadcast controller for manual testing.

**Usage:**
```bash
python UART/broadcast_controller.py
```

**Features:**
- Manual 15-byte broadcast input
- Real-time packet validation
- Continuous operation until quit

**Example:**
```
Input 15 byte HEX: 0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF

Broadcast sent (15 bytes):
  0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF
```

### single_device_sweep.py
Automated angular sweep test for a single device.

**Usage:**
```bash
python UART/single_device_sweep.py
```

**Configuration:**
```python
DEVICE_ID = 1       # Target device (1-5)
STEP_DEGREE = 15    # Angular increment (degrees)
DELAY_BETWEEN = 2   # Delay between steps (seconds)
```

**Operation:**
- Sweeps from 0° to 360° in configurable steps
- Target device rotates, others remain at 0°
- Displays packet data and device responses

### multi_device_sweep.py
Synchronized multi-device angular sweep.

**Usage:**
```bash
python UART/multi_device_sweep.py
```

**Features:**
- All 5 devices sweep simultaneously
- Configurable step size and delay
- Synchronized motion patterns

### choreographed_demo.py
Pre-programmed choreographed motion demonstration.

**Usage:**
```bash
python UART/choreographed_demo.py
```

**Patterns:**
- Sequential activation
- Wave motion
- Synchronized rotation
- Custom choreography

## Firmware Structure

### Key Files

**STM32 Project:**
```
Digital_Syncro_ROME_0.1/
├── Inc/
│   ├── main.h              # Device ID, protocol constants
│   ├── dsc_rome_16b.h      # GPIO control interface
│   └── fonts.h             # OLED font definitions
├── Src/
│   ├── main.c              # Main loop, UART parsing, protocol handling
│   ├── dsc_rome_16b.c      # 16-bit digital output to GPIO
│   └── ssd1306.c           # OLED display driver
```

### Protocol Implementation

**Broadcast Parsing (main.c):**
```c
// Parse 15 HEX bytes from UART
while(token != NULL && byte_index < 15){
  bytes[byte_index] = (uint8_t)strtol(token, NULL, 16);
  token = strtok(NULL, " ");
  byte_index++;
}

// Validate header
if(bytes[0] != 0xA5 || bytes[1] != 0x99){
  // Silently discard
  return;
}

// Extract device data
int data_index = 5 + (DEVICE_ID - 1) * 2;
uint8_t byte_high = bytes[data_index];
uint8_t byte_low = bytes[data_index + 1];
digital_val = (uint16_t)((byte_high << 8) | byte_low);
```

**GPIO Output (dsc_rome_16b.c):**
```c
void dsc(uint16_t digital){
  // Set 16 GPIO pins according to bit pattern
  if(digital & 0x0001) HAL_GPIO_WritePin(B1_GPIO_Port, B1_Pin, SET);
  else HAL_GPIO_WritePin(B1_GPIO_Port, B1_Pin, RESET);
  // ... repeat for bits 1-15
}
```

## Performance Optimizations

### Timing Improvements
- **GPIO delays removed:** No blocking delays in `dsc()` function
- **LED blink reduced:** 20ms (from 100ms) to minimize UART blocking
- **Response time:** <50ms per broadcast packet
- **Max throughput:** ~20 broadcasts/second

### Memory Efficiency
- **Buffer size:** 90 bytes (accommodates 15-byte broadcast as ASCII HEX)
- **Silent error handling:** Invalid packets discarded without response
- **Minimal UART traffic:** Only valid data acknowledged

## Development Roadmap

### Current Status
- [x] 15-byte broadcast protocol implemented
- [x] Header validation functional
- [x] Multi-device support (1-5 devices)
- [x] Test scripts for validation
- [x] Performance optimizations

### Next Phase: Raspberry Pi Integration
- [ ] Port Python scripts to Raspberry Pi 3B
- [ ] Implement production control software
- [ ] Add error recovery mechanisms
- [ ] Performance profiling on Raspberry Pi
- [ ] Field testing with actual synchro motors

## Building and Flashing

### STM32 Firmware

**Requirements:**
- STM32CubeIDE or compatible toolchain
- ST-Link programmer

**Steps:**
1. Open project in STM32CubeIDE
2. Configure `DEVICE_ID` in `Inc/main.h` (1-5)
3. Build project
4. Flash to STM32 via ST-Link

### Python Scripts

**Requirements:**
```bash
pip install pyserial
```

**Configuration:**
Edit serial port in each script:
```python
PORT = 'COM11'  # Windows
# PORT = '/dev/ttyUSB0'  # Linux/Raspberry Pi
BAUD = 115200
```

## Troubleshooting

### No Response from Device
- Check serial port configuration
- Verify DEVICE_ID matches target device
- Ensure 115200 baud rate
- Confirm header bytes are `0xA5 0x99`

### Motor Position Incorrect
- Verify byte order (MSB/LSB)
- Check GPIO pin mapping
- Confirm digital-to-synchro converter configuration
- Validate position encoding formula

### Packet Loss
- Reduce broadcast rate
- Check UART buffer size
- Verify cable quality
- Monitor for electrical noise

## License

This project is developed for the DSC-ROME test bench system.

## Contact

For technical questions regarding protocol implementation or Raspberry Pi integration, refer to project documentation.
