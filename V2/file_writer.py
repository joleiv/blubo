import sys
import time
from datetime import datetime

class FileWriter:
    def __init__(self):
        self.header_info = """
#HEADER
# Device type: 
# Instrument ID: 
# Data supplier:
# Location name: 
# Position: 
# Local timezone: UTC
# Time Synchronization: 
# Moving / Stationary position: STATIONARY
# Moving / Fixed look direction:
# Number of channels:3
# Filters per channel:1
# Measurement direction per channel: 
# Field of view:
# Number of fields per line: 
# Device specific characteristics:
# UTC Date & Time, Local Date & Time, R, G, B meanADU 
# YYYY-MM-DDTHH:mm:ss.fff;YYYY-M
# END OF HEADER"""

        self.start_time_str = time.strftime("%Y%m%dT%H%M%S")
        self.filename1 = f'{self.start_time_str}_SKYGLOW_LABSENS.txt'
        self.filename2 = f'{self.start_time_str}_SECOND_SKYGLOW_LABSENS.txt'
        
        try:
            with open(self.filename1, 'w') as f:
                f.write('tiempo (unix-time), canal 1 (counts), canal 2 (counts), canal 3 (counts), tsl (lux)\n')
            with open(self.filename2, 'w') as f:
                f.write(f'{self.header_info}\n')
        except Exception as e:
            print(f"Error initializing files: {e}")
            sys.exit(1)
    
    def write_data(self, timestamp, values):
        utc_formato = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        local_formato = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

        with open(self.filename1, 'a') as f:
            f.write(f'{timestamp},{values[0]},{values[1]},{values[2]}\n')

        with open(self.filename2, 'a') as f:
            f.write(utc_formato + ";" + local_formato + ";" + ";".join(map(str, values)) + "\n")