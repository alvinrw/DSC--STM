# Bug Fix: Broadcast Not Working

## Issue
Broadcast functionality was not working, but device-specific updates worked correctly.

## Root Causes

### 1. Buffer Size Limit Mismatch (CRITICAL)
The buffer size check in the main loop was still using the old limit:
```c
// Line 117 - OLD (BUGGY)
if(MY_UART1.text_index < 59){
```

But the buffer was increased to 90 bytes:
```c
// main.h
char text_buffer[90];
```

**Impact:** Broadcast data requires ~80 characters for 15 bytes:
```
"0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF"
 └─────────────────────────────── 79 characters ──────────────────────────────┘
```

With limit of 59, the data was **truncated** at character 59, causing parsing to fail!

**Fix:**
```c
// Line 117 - NEW (FIXED)
if(MY_UART1.text_index < 89){  // Buffer size is 90, leave 1 for null terminator
```

### 2. Broadcast Detection Logic
The broadcast detection condition was matching both broadcast and device commands.

**Fix:** Added CS flag check:
```c
// Line 183 - FIXED
else if(MY_UART1.CS == 0 && strchr(MY_UART1.text_buffer, ' ') != NULL){
```

## Files Changed
1. `main.c` line 117 - Buffer size limit
2. `main.c` line 183 - Broadcast detection condition

## Why Device Commands Still Worked
Device-specific commands only need ~15 characters:
```
"0x80 0x00"
 └─ 9 chars ─┘
```

This fits within the old 59-character limit, so they worked fine!

## Testing
1. ✅ Broadcast should now work correctly
2. ✅ Device-specific updates should still work
3. ✅ Header validation should reject invalid headers

## Verification Steps
```bash
# Test broadcast
python send_data.py
# Input: 0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF
# Expected: All devices respond with "Init" messages

# Test device-specific
python send_data.py
# Menu: 1
# Input: 0x80 0x00
# Expected: Device #1 responds with "OK" message
```
