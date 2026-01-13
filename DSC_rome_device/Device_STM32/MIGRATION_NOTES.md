# Device STM32 Firmware - Migration Notes

## Status: ✅ **EXISTING CODE - NEEDS MODIFICATION**

The current firmware in `Digital_Syncro_ROME_0.1/` will be adapted for Device STM32.

---

## Current Implementation

### What Works:
- ✅ OLED display (SSD1306)
- ✅ GPIO 16-bit output
- ✅ Encoding logic (×10, relative course for Device #5)
- ✅ DEVICE_ID configuration
- ✅ LED status indicator

### What Needs to Change:
- ❌ **UART reception from Raspi** → Change to **I2C reception from Master**
- ❌ **Binary packet parsing (15 bytes)** → Change to **3-byte I2C packet**
- ❌ **Header validation (0xA5 0x99)** → Change to **start marker (0xAA)**

---

## Required Changes

### 1. Remove UART Reception Code

**Delete:**
```c
// Lines ~110-210 in main.c
// All UART polling and packet reception logic
uint8_t rx_buffer[15];
HAL_UART_Receive(&huart1, &received_byte, 1, 10);
// ... header validation, packet assembly
```

### 2. Add I2C Slave Reception

**Add:**
```c
// I2C slave configuration
#define I2C_DEVICE_ADDRESS (0x10 + (DEVICE_ID - 1))  // 0x10-0x14

// Reception buffer
uint8_t i2c_rx_buffer[3];

// I2C callback
void HAL_I2C_SlaveRxCpltCallback(I2C_HandleTypeDef *hi2c) {
  if(i2c_rx_buffer[0] == 0xAA) {  // Validate start marker
    uint16_t digital_val = (i2c_rx_buffer[1] << 8) | i2c_rx_buffer[2];
    
    // Apply encoding (existing code)
    // Update OLED (existing code)
    // Update GPIO (existing code)
  }
  
  // Re-enable reception
  HAL_I2C_Slave_Receive_IT(&hi2c1, i2c_rx_buffer, 3);
}
```

### 3. Update main.h

**Add I2C address configuration:**
```c
// I2C Configuration
#define I2C_OWN_ADDRESS (0x10 + (DEVICE_ID - 1))  // 0x10-0x14
```

### 4. Keep Existing Logic

**No changes needed:**
- Encoding formulas (lines ~155-175)
- OLED display (lines ~177-187)
- GPIO output (line ~190)
- LED blink (lines ~192-196)
- UART transmit for debug (lines ~198-208)

---

## STM32CubeIDE Configuration

### I2C1 (Master Communication):
- **Mode**: I2C Slave
- **Own Address**: `0x10 + (DEVICE_ID - 1)`
- **Speed**: 100kHz
- **Pins**: PB6 (SCL), PB7 (SDA)

### I2C2 (OLED Display):
- **Mode**: I2C Master
- **Speed**: 400kHz
- **Pins**: PB8 (SCL), PB9 (SDA)
- **Keep existing configuration**

### GPIO:
- **Keep existing 16-bit output**
- **Keep LED on PC13**

---

## Migration Steps

1. **Copy project to Device_STM32/**
   ```bash
   xcopy Digital_Syncro_ROME_0.1 Device_STM32\ /E /I
   ```

2. **Open in STM32CubeIDE**
   - File → Open Projects from File System
   - Select `Device_STM32/`

3. **Configure I2C1 as Slave**
   - Open .ioc file
   - Enable I2C1, set as Slave
   - Set own address based on DEVICE_ID

4. **Modify main.c**
   - Remove UART reception (lines ~110-210)
   - Add I2C slave reception
   - Keep encoding and display logic

5. **Test**
   - Build and flash
   - Test with simulated Master (Arduino/PC)
   - Verify OLED updates

---

## Testing Without Master

Use Arduino or USB-I2C adapter to simulate Master:

```python
# Python with USB-I2C adapter
import smbus
bus = smbus.SMBus(1)

# Send to Device #1 (Pitch = 90°)
# 90 × 10 = 900 = 0x0384
bus.write_i2c_block_data(0x10, 0xAA, [0x03, 0x84])
```

---

## Next Steps

1. Copy existing firmware to Device_STM32/
2. Modify I2C configuration
3. Update main.c for I2C reception
4. Test with simulated Master
5. Flash to all 5 Device STM32s with different DEVICE_IDs
