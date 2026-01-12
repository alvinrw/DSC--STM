import serial
import time
from datetime import datetime
import os

# Konfigurasi serial port
PORT = 'COM17'  # Sesuaikan dengan port kamu
BAUD = 115200

# Konfigurasi logging
ENABLE_LOGGING = True
LOG_DIR = "logs"

class SerialMonitor:
    def __init__(self, port, baud, enable_logging=True):
        self.port = port
        self.baud = baud
        self.enable_logging = enable_logging
        self.log_file = None
        self.stats = {
            'broadcasts': 0,
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
        log_filename = f"{LOG_DIR}/serial_log_{timestamp}.txt"
        self.log_file = open(log_filename, 'w', encoding='utf-8')
        self.log_file.write(f"Serial Monitor Log - Started at {datetime.now()}\n")
        self.log_file.write(f"Port: {self.port}, Baud: {self.baud}\n")
        self.log_file.write("=" * 80 + "\n\n")
        print(f"✓ Logging to: {log_filename}")
    
    def parse_line(self, line):
        """Parse response dari STM32"""
        if "Broadcast received" in line:
            self.stats['broadcasts'] += 1
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
                    'syncro': syncro_val,
                    'raw': line
                }
            except:
                return "UNKNOWN", line
        elif "Invalid" in line or "Error" in line:
            self.stats['errors'] += 1
            return "ERROR", line
        else:
            return "INFO", line
    
    def format_output(self, msg_type, data):
        """Format output dengan timestamp dan warna"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
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
        else:
            icon = "  "
            prefix = "UNKNOWN"
            message = str(data)
        
        return f"[{timestamp}] {icon} {prefix:12s} | {message}"
    
    def log_message(self, formatted_msg):
        """Log message ke file dan console"""
        print(formatted_msg)
        if self.log_file:
            self.log_file.write(formatted_msg + "\n")
            self.log_file.flush()
    
    def print_stats(self):
        """Print statistik monitoring"""
        print("\n" + "=" * 80)
        print("STATISTICS:")
        print(f"  Total Messages    : {self.stats['total_messages']}")
        print(f"  Broadcasts        : {self.stats['broadcasts']}")
        print(f"  Device Updates    : {self.stats['device_updates']}")
        print(f"  Errors            : {self.stats['errors']}")
        print("=" * 80)
    
    def run(self):
        """Main monitoring loop"""
        try:
            # Buka koneksi serial
            ser = serial.Serial(self.port, self.baud, timeout=1)
            print(f"✓ Connected to {self.port} at {self.baud} baud")
            print(f"✓ Listening for data from STM32...")
            print("=" * 80)
            print("Press Ctrl+C to stop\n")
            
            time.sleep(2)
            ser.reset_input_buffer()
            
            # Loop membaca data
            while True:
                if ser.in_waiting > 0:
                    try:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        
                        if line:
                            self.stats['total_messages'] += 1
                            msg_type, data = self.parse_line(line)
                            output = self.format_output(msg_type, data)
                            self.log_message(output)
                            
                    except UnicodeDecodeError:
                        error_msg = f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  DECODE_ERROR | Unicode decode failed"
                        self.log_message(error_msg)
                    except Exception as e:
                        error_msg = f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  PARSE_ERROR  | {e}"
                        self.log_message(error_msg)
                
                time.sleep(0.01)
        
        except serial.SerialException as e:
            print(f"\n❌ Serial Error: {e}")
            print(f"Pastikan port {self.port} benar dan tidak digunakan program lain!")
        except KeyboardInterrupt:
            print("\n\n✓ Stopped by user")
            self.print_stats()
        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()
                print("✓ Serial connection closed")
            if self.log_file:
                self.log_file.close()
                print("✓ Log file closed")

if __name__ == "__main__":
    monitor = SerialMonitor(PORT, BAUD, ENABLE_LOGGING)
    monitor.run()
