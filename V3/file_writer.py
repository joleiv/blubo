import sys
import time
from datetime import datetime
import socket
import os

class FileWriter:
    def __init__(self, config, last_rtc_update):
        # Obtener hostname y extraer el Instrument ID
        hostname = socket.gethostname()
        instrument_id = ''.join(filter(str.isdigit, hostname))
        if not instrument_id:
            instrument_id = "Unknown"

        device_type = "blubo"
        data_supplier = config.get("data_supplier", "")
        location_name = config.get("location_name", "")
        position = config.get("position", "")

        # Crear el header dinámicamente
        self.header_info = f"""
#HEADER
# Device type: {device_type}
# Instrument ID: {instrument_id}
# Data supplier: {data_supplier}
# Location name: {location_name}
# Position: {position}
# Local timezone: UTC
# Time Synchronization: Last RTC Update: {last_rtc_update}
# Moving / Stationary position: STATIONARY
# Moving / Fixed look direction: FIXED
# Number of channels: 3
# Filters per channel: 1
# Measurement direction per channel: 
# Field of view:
# Number of fields per line: 
# Device specific characteristics:
# UTC Date & Time, Local Date & Time, R, G, B meanADU 
# YYYY-MM-DDTHH:mm:ss.fff;YYYY-M
# END OF HEADER"""

        # Crear la carpeta /blubo/data si no existe
        base_dir = "/blubo/data"
        os.makedirs(base_dir, exist_ok=True)

        # Usar la fecha actual para el nombre base del archivo (un archivo por día)
        date_str = datetime.utcnow().strftime("%Y%m%d")  # fecha UTC o local, como prefieras
        
        # Crear el nombre base del archivo
        # Formato: YYYYMMDD_BLUBO{instrument_id}.txt
        base_filename = f"{date_str}_BLUBO{instrument_id}.txt"
        file_path = os.path.join(base_dir, base_filename)

        # Si el archivo ya existe, agregar sufijos numéricos ascendentes
        # Ejemplo: YYYYMMDD_1_BLUBO6.txt, YYYYMMDD_2_BLUBO6.txt, etc.
        count = 1
        while os.path.exists(file_path):
            file_path = os.path.join(base_dir, f"{date_str}_{count}_BLUBO{instrument_id}.txt")
            count += 1

        self.filename = file_path

        try:
            with open(self.filename, 'w') as f:
                # Escribimos el header
                f.write(self.header_info + "\n")
        except Exception as e:
            print(f"Error initializing file: {e}")
            sys.exit(1)

    def write_data(self, timestamp, values):
        utc_formato = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        local_formato = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

        # Escribir datos en el archivo principal
        with open(self.filename, 'a') as f:
            # Formato: UTC;Local;values
            # values son R, G, B meanADU, adaptarlo si es necesario
            f.write(utc_formato + ";" + local_formato + ";" + ";".join(map(str, values)) + "\n")