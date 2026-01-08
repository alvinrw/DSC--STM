# 15-Byte Broadcast Protocol - Quick Reference

## Protocol Structure

```
Byte:  1    2    3    4    5    6    7    8    9   10   11   12   13   14   15
      ┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
      │0xA5│0x99│ -- │ -- │ -- │ D1 │ D1 │ D2 │ D2 │ D3 │ D3 │ D4 │ D4 │ D5 │ D5 │
      └────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
       Header    Reserved      Device #1   Device #2   Device #3   Device #4   Device #5
      (Required) (Ignored)     (2 bytes)   (2 bytes)   (2 bytes)   (2 bytes)   (2 bytes)
```

## Example Broadcast

**User Input (send_data.py):**
```
0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF
```

**Result:**
- Device #1: 0° (0x0000 = 0)
- Device #2: 90° (0x4000 = 16384)
- Device #3: 180° (0x8000 = 32768)
- Device #4: 270° (0xC000 = 49152)
- Device #5: 360° (0xFFFF = 65535)

## HEX to Degree Mapping (Every 5°)

| Degree | HEX Value | Decimal |
|--------|-----------|---------|
| 0° | 0x0000 | 0 |
| 5° | 0x038E | 910 |
| 10° | 0x071C | 1820 |
| 15° | 0x0AAB | 2731 |
| 20° | 0x0E39 | 3641 |
| 45° | 0x2000 | 8192 |
| 90° | 0x4000 | 16384 |
| 135° | 0x6000 | 24576 |
| 180° | 0x8000 | 32768 |
| 225° | 0xA000 | 40960 |
| 270° | 0xC000 | 49152 |
| 315° | 0xE000 | 57344 |
| 360° | 0xFFFF | 65535 |

**Formula:** `HEX = (Degree / 360) × 65535`

## Usage

### Broadcast (All Devices)
```bash
python send_data.py
# Menu: 0
# Input: 0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF
```

### Single Device Update
```bash
python send_data.py
# Menu: 1 (for Device #1)
# Input: 0x80 0x00  (180°)
```

## Error Messages

| Message | Cause | Solution |
|---------|-------|----------|
| `Expected 15 bytes, got X` | Incomplete packet | Send exactly 15 bytes |
| `Invalid header (0xXX 0xXX)` | Wrong header | First 2 bytes must be 0xA5 0x99 |
| `Dev#X OK: ...` | Success | Device updated successfully |

## Files Modified

- `main.h` - Added protocol constants, increased buffer
- `main.c` - Updated broadcast parsing with validation
- `send_data.py` - Auto-insert header and reserved bytes
- `test_simple.py` - Updated test cases
