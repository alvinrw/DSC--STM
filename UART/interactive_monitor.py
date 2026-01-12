import serial
import time
import threading
from datetime import datetime
import os

# Konfigurasi serial port
PORT = 'COM17'  # Sesuaikan dengan port kamu
BAUD = 115200

# Konfigurasi logging
ENABLE_LOGGING = True
LOG_DIR = "logs"

class InteractiveSerialMonitor:
    def __init__(self, port, baud, enable_logging=True):
        self.port = port
        self.baud = baud
        self.enable_logging = enable_logging
        self.log_file = None
        self.ser = None
        self.running = False
        self.stats = {
            'broadcasts_received': 0,
            'broadcasts_sent': 0,
            'device_updates': 0,
            'errors': 0,
            'total_messages': 0
        }
        
        if self.enable_logging:
            self._setup_logging()
    
    def _setup_logging(self):
        """Setup log file dengan timestamp"""
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{LOG_DIR}/interactive_log_{timestamp}.txt"
        self.log_file = open(log_filename, 'w', encoding='utf-8')
        self.log_file.write(f"Interactive Serial Monitor Log - Started at {datetime.now()}\n")
        self.log_file.write(f"Port: {self.port}, Baud: {self.baud}\n")
        self.log_file.write("=" * 80 + "\n\n")
        print(f"✓ Logging to: {log_filename}")
    
    def parse_line(self, line):
        """Parse response dari STM32"""
        if "Broadcast received" in line:
            self.stats['broadcasts_received'] += 1
            return "BROADCAST", line
        elif "Device" in line and "Digital:" in line:
            self.stats['device_updates'] += 1
            try:
                parts = line.split('-')
                device_part = parts[0].strip()
                data_part = parts[1].strip()
                
                device_num = device_part.split()[1]
                digital_val = data_part.split(',')[0].split(':')[1].strip()
                syncro_val = data_part.split(',')[1].split(':')[1].strip()
                
                return "DEVICE_DATA", {
                    'device': device_num,
                    'digital': digital_val,
                    'syncro': syncro_val
                }
            except:
                return "UNKNOWN", line
        elif "Invalid" in line or "Error" in line:
            self.stats['errors'] += 1
            return "ERROR", line
        else:
            return "INFO", line
    
    def format_output(self, msg_type, data, direction="RX"):
        """Format output dengan timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        arrow = "←" if direction == "RX" else "→"
        
        if msg_type == "BROADCAST":
            icon = "📡"
            prefix = "BROADCAST"
            message = data
        elif msg_type == "DEVICE_DATA":
            icon = "📊"
            prefix = f"DEV#{data['device']}"
            message = f"Digital: {data['digital']:>5s} | Syncro: {data['syncro']}"
        elif msg_type == "ERROR":
            icon = "❌"
            prefix = "ERROR"
            message = data
        elif msg_type == "INFO":
            icon = "ℹ️ "
            prefix = "INFO"
            message = data
        elif msg_type == "SENT":
            icon = "📤"
            prefix = "SENT"
            message = data
        else:
            icon = "  "
            prefix = "UNKNOWN"
            message = str(data)
        
        return f"[{timestamp}] {arrow} {icon} {prefix:12s} | {message}"
    
    def log_message(self, formatted_msg):
        """Log message ke file dan console"""
        print(formatted_msg)
        if self.log_file:
            self.log_file.write(formatted_msg + "\n")
            self.log_file.flush()
    
    def read_serial_thread(self):
        """Thread untuk membaca data dari serial"""
        while self.running:
            if self.ser and self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if line:
                        self.stats['total_messages'] += 1
                        msg_type, data = self.parse_line(line)
                        output = self.format_output(msg_type, data, "RX")
                        self.log_message(output)
                        
                except UnicodeDecodeError:
                    error_msg = f"[{datetime.now().strftime('%H:%M:%S')}] ← ⚠️  DECODE_ERROR | Unicode decode failed"
                    self.log_message(error_msg)
                except Exception as e:
                    error_msg = f"[{datetime.now().strftime('%H:%M:%S')}] ← ⚠️  PARSE_ERROR  | {e}"
                    self.log_message(error_msg)
            
            time.sleep(0.01)
    
    def parse_hex_input(self, input_str):
        """Parse input HEX dan validasi - support partial input"""
        parts = input_str.strip().split()
        hex_values = []
        
        for part in parts:
            if not part.startswith('0x') and not part.startswith('0X'):
                part = '0x' + part
            
            try:
                val = int(part, 16)
                if val < 0 or val > 255:
                    return None, f"Nilai {part} harus 0x00-0xFF!"
                hex_values.append(part)
            except ValueError:
                return None, f"Format HEX salah: {part}"
        
        # Auto-complete dengan 0x00 jika kurang dari 15 bytes
        if len(hex_values) > 0 and len(hex_values) < 15:
            # Pastikan header ada
            if len(hex_values) >= 2:
                if hex_values[0].upper() != '0XA5' or hex_values[1].upper() != '0X99':
                    return None, "Header harus dimulai dengan 0xA5 0x99!"
            else:
                # Jika cuma 1 byte atau kosong, tambahkan header
                if len(hex_values) == 0:
                    hex_values = ['0xA5', '0x99']
                elif len(hex_values) == 1:
                    return None, "Minimal 2 bytes untuk header (0xA5 0x99)!"
            
            # Fill sisanya dengan 0x00
            while len(hex_values) < 15:
                hex_values.append('0x00')
            
            info_msg = self.format_output("INFO", f"Auto-completed to 15 bytes (filled with 0x00)", "TX")
            self.log_message(info_msg)
        
        return hex_values, None
    
    def send_broadcast(self, hex_values):
        """Kirim broadcast 15 bytes ke semua device"""
        # Validasi sudah dilakukan di parse_hex_input
        if len(hex_values) != 15:
            error_msg = self.format_output("ERROR", f"Internal error: Expected 15 bytes, got {len(hex_values)}", "TX")
            self.log_message(error_msg)
            return False
        
        data = " ".join(hex_values) + "\n"
        self.ser.write(data.encode())
        
        sent_msg = self.format_output("SENT", data.strip(), "TX")
        self.log_message(sent_msg)
        self.stats['broadcasts_sent'] += 1
        
        time.sleep(0.1)
        return True
    
    def print_help(self):
        """Print help menu"""
        print("\n" + "=" * 80)
        print("COMMANDS:")
        print("  <HEX bytes>     : Send broadcast (auto-completes to 15 bytes)")
        print("  help            : Show this help")
        print("  stats           : Show statistics")
        print("  clear           : Clear screen")
        print("  quit / q        : Exit program")
        print("\nEXAMPLES:")
        print("  Full broadcast (15 bytes):")
        print("    0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF")
        print("\n  Partial input (auto-fills with 0x00):")
        print("    0xA5 0x99 0x00 0x00 0x00 0x00 0x00")
        print("    → Auto-completed: 0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00")
        print("\n  Set Device #2 to 90° (0x4000):")
        print("    0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00")
        print("    → Devices #3-5 will be 0x0000 (0°)")
        print("=" * 80)
    
    def print_stats(self):
        """Print statistik monitoring"""
        print("\n" + "=" * 80)
        print("STATISTICS:")
        print(f"  Total Messages       : {self.stats['total_messages']}")
        print(f"  Broadcasts Received  : {self.stats['broadcasts_received']}")
        print(f"  Broadcasts Sent      : {self.stats['broadcasts_sent']}")
        print(f"  Device Updates       : {self.stats['device_updates']}")
        print(f"  Errors               : {self.stats['errors']}")
        print("=" * 80)
    
    def print_header(self):
        """Print header informasi"""
        print("\n" + "=" * 80)
        print("  INTERACTIVE SERIAL MONITOR - DSC-STM")
        print("=" * 80)
        print("\nProtokol 15-Byte:")
        print("  Byte 1-2   : Header (0xA5 0x99) - WAJIB!")
        print("  Byte 3-5   : Reserved (0x00 0x00 0x00)")
        print("  Byte 6-15  : Device data (2 byte × 5 devices)")
        print("\nFormat:")
        print("  0xA5 0x99 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH 0xHH")
        print("  └─────────┘ └───────────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘")
        print("    Header      Reserved    Dev#1   Dev#2   Dev#3   Dev#4   Dev#5")
        print("\nContoh:")
        print("  0xA5 0x99 0x00 0x00 0x00 0x00 0x00 0x40 0x00 0x80 0x00 0xC0 0x00 0xFF 0xFF")
        print("  (Dev#1=0°, Dev#2=90°, Dev#3=180°, Dev#4=270°, Dev#5=360°)")
        print("\nKetik 'help' untuk command list")
        print("=" * 80 + "\n")
    
    def run(self):
        """Main program loop"""
        try:
            # Buka koneksi serial
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            print(f"✓ Connected to {self.port} at {self.baud} baud")
            time.sleep(2)
            self.ser.reset_input_buffer()
            
            # Start reading thread
            self.running = True
            read_thread = threading.Thread(target=self.read_serial_thread, daemon=True)
            read_thread.start()
            
            # Print header
            self.print_header()
            
            # Main input loop
            while True:
                try:
                    user_input = input("\n> ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.lower() in ['quit', 'q', 'exit']:
                        break
                    elif user_input.lower() == 'help':
                        self.print_help()
                    elif user_input.lower() == 'stats':
                        self.print_stats()
                    elif user_input.lower() == 'clear':
                        os.system('cls' if os.name == 'nt' else 'clear')
                        self.print_header()
                    else:
                        # Parse dan kirim broadcast
                        hex_values, error = self.parse_hex_input(user_input)
                        
                        if error:
                            error_msg = self.format_output("ERROR", error, "TX")
                            self.log_message(error_msg)
                        else:
                            self.send_broadcast(hex_values)
                
                except KeyboardInterrupt:
                    print("\n")
                    break
                except Exception as e:
                    error_msg = self.format_output("ERROR", f"Input error: {e}", "TX")
                    self.log_message(error_msg)
            
            # Cleanup
            self.running = False
            time.sleep(0.1)
            print("\n✓ Stopped by user")
            self.print_stats()
            
        except serial.SerialException as e:
            print(f"\n❌ Serial Error: {e}")
            print(f"Pastikan port {self.port} benar dan tidak digunakan program lain!")
        finally:
            self.running = False
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("✓ Serial connection closed")
            if self.log_file:
                self.log_file.close()
                print("✓ Log file closed")

if __name__ == "__main__":
    monitor = InteractiveSerialMonitor(PORT, BAUD, ENABLE_LOGGING)
    monitor.run()
