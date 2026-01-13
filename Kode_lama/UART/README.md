# UART Test Scripts

Python scripts for testing and validating the 15-byte broadcast protocol.

## Scripts Overview

### broadcast_controller.py
Interactive controller for manual broadcast testing.

**Usage:**
```bash
python broadcast_controller.py
```

**Features:**
- Manual 15-byte HEX input
- Real-time validation
- Continuous operation

### single_device_sweep.py
Automated angular sweep for single device testing.

**Configuration:**
```python
DEVICE_ID = 1       # Target device (1-5)
STEP_DEGREE = 15    # Angular increment
DELAY_BETWEEN = 2   # Delay between steps (seconds)
```

**Usage:**
```bash
python single_device_sweep.py
```

### multi_device_sweep.py
Synchronized multi-device angular sweep.

**Usage:**
```bash
python multi_device_sweep.py
```

**Features:**
- All 5 devices sweep simultaneously
- Configurable patterns
- Synchronized motion

### choreographed_demo.py
Pre-programmed motion demonstration.

**Usage:**
```bash
python choreographed_demo.py
```

**Patterns:**
- Sequential activation
- Wave motion
- Synchronized rotation

## Configuration

All scripts use the same serial configuration:

```python
PORT = 'COM11'  # Change to your serial port
BAUD = 115200
```

For Raspberry Pi, change to:
```python
PORT = '/dev/ttyUSB0'  # or /dev/ttyAMA0
```

## Requirements

```bash
pip install pyserial
```

## Protocol Format

All scripts send 15-byte broadcast packets:

```
0xA5 0x99 0x00 0x00 0x00 [Dev1] [Dev2] [Dev3] [Dev4] [Dev5]
```

Where each device data is 2 bytes (16-bit position value).
