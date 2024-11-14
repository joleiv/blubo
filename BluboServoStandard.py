import pigpio
import time
from datetime import datetime
import signal
import sys
import board
import busio
import threading
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from Adafruit_IO import MQTTClient
import subprocess
import logging
from os import system
import RPi.GPIO as GPIO
import time

def check_pigpiod():
    try:
        subprocess.check_output(["pidof", "pigpiod"])
        return True
    except subprocess.CalledProcessError:
        return False
    
if not check_pigpiod():
    print("'pigpiod' esta desactivado")
    sys.exit(1)

# Configuración
SERVO_PIN = 13
ADAFRUIT_AIO_USERNAME = "blubo"
ADAFRUIT_AIO_KEY = "aio_LNaD94EBm2Xx70S8YfizyLUJI84A"
MAX_RECONNECTION_ATTEMPTS = 10
CHECK_WIFI_INTERVAL = 60  # seconds
PUBLISH_INTERVAL = 15  # seconds
TIME_TO_CLOSE_START = "08:00:00"
TIME_TO_CLOSE_END = "17:30:00"
FILE_HEADER = 'tiempo (unix-time), canal 1 (counts), canal 2 (counts), canal 3 (counts)\n'
PING_SERVER = "8.8.8.8"  # Google DNS server
file_open = False
baconFile = None
current_filename = None
header_info = """
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
        

# Configuración de registro
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicializar PWM para el servo
pwm = pigpio.pi()

def set_servo_angle(angle):
    pulse_width = int((angle / 180.0) * (2500 - 500) + 500)
    pwm.set_servo_pulsewidth(SERVO_PIN, pulse_width)

def is_time_to_close():
    now = datetime.now().time()
    start_time = datetime.strptime(TIME_TO_CLOSE_START, "%H:%M:%S").time()
    end_time = datetime.strptime(TIME_TO_CLOSE_END, "%H:%M:%S").time()
    return start_time <= now <= end_time

def disconnected(client):
    print('Desconectado de Adafruit IO!')

# Inicializar cliente MQTT
client = MQTTClient(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)
client.connect()
time.sleep(1)
client.loop_background()

# Inicializar ADS1115
def init_ads():
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c, address=0x49)
        return [AnalogIn(ads, ADS.P0), AnalogIn(ads, ADS.P1), AnalogIn(ads, ADS.P2)]
    except Exception as e:
        logging.error(f"Error initializing ADS: {e}")
        sys.exit(1)

channels = init_ads()

def signal_handler(sig, frame):
    print('\nKill command received from keyboard - script exiting')
    pwm.set_servo_pulsewidth(SERVO_PIN, 0)
    time.sleep(1)
    sys.exit(0)

# Inicializar archivos
try:
    tiempo_inicio = time.strftime("%Y%m%dT%H%M%S")
    with open(f'{tiempo_inicio}_SKYGLOW_LABSENS.txt', 'w') as baconFile1:
        baconFile1.write('tiempo (unix-time), canal 1 (counts), canal 2 (counts), canal 3 (counts), tsl (lux)\n')

    with open(f'{tiempo_inicio}_SECOND_SKYGLOW_LABSENS.txt', 'w') as baconFile2:
        baconFile2.write(f'{header_info}\n')

except Exception as e:
    print(f"Error initializing files: {e}")
    sys.exit(1)

# Función para escribir en los archivos
def write_to_files(timestamp, values):
    utc_formato = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    local_formato = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    
    # Escribir en el primer archivo
    with open(f'{tiempo_inicio}_SKYGLOW_LABSENS.txt', 'a') as baconFile1:
        baconFile1.write(f'{timestamp},{values[0]},{values[1]},{values[2]}\n')
    
    # Escribir en el segundo archivo
    with open(f'{tiempo_inicio}_SECOND_SKYGLOW_LABSENS.txt', 'a') as baconFile2:
        baconFile2.write(utc_formato + ";" + local_formato + ";" + ";".join(map(str, values)) + "\n")


signal.signal(signal.SIGINT, signal_handler)

def ping_server(server):
    try:
        response = subprocess.run(['ping', '-c', '1', server], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return response.returncode == 0
    except Exception as e:
        logging.error(f"Error executing ping: {e}")
        return False

def check_wifi_connection(client):
    reconnection_attempts = 0
    while True:
        if not ping_server(PING_SERVER):
            logging.warning("No internet connection. Attempting to reconnect...")
            while reconnection_attempts < MAX_RECONNECTION_ATTEMPTS:
                try:
                    if not client.is_connected():
                        client = MQTTClient(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)
                        client.connect()
                        logging.info('Reconexión exitosa a Adafruit IO')
                    break
                except Exception as e:
                    logging.error(f"Error al intentar reconectar a Adafruit IO: {e}")
                    reconnection_attempts += 1
                    logging.info(f'Intento de reconexión número {reconnection_attempts}/{MAX_RECONNECTION_ATTEMPTS}.')
                    time.sleep(30)
            else:
                logging.warning('No se pudo reconectar después de varios intentos. Continuando sin conexión a Adafruit IO.')
        else:
            if not client.is_connected():
                try:
                    client.connect()
                    logging.info('Reconexión exitosa a Adafruit IO')
                except Exception as e:
                    logging.error(f"Error al intentar reconectar a Adafruit IO: {e}")
        time.sleep(CHECK_WIFI_INTERVAL)

def wifi_reconnection_thread():
    threading.Thread(target=check_wifi_connection, args=(client,), daemon=True).start()

def main():
    # Iniciar hilo de reconexión de WiFi
    wifi_reconnection_thread()
    
    tiempo_ultima_publicacion = time.time()
    
    while True:
        try:
            timestamp = time.time()
            values = [chan.value for chan in channels]
            voltages = ["%0.4f" % chan.voltage for chan in channels]

            print("\t\t\tCH01\tCH02\tCH03")
            print(f'{time.strftime("[%Y-%m-%d %H:%M:%S]")}\t{voltages[0]}\t{voltages[1]}\t{voltages[2]}')
            
            write_to_files(timestamp, values)

            if time.time() - tiempo_ultima_publicacion >= PUBLISH_INTERVAL:
                if client.is_connected():
                    try:
                        for i, value in enumerate(values, start=1):
                            client.publish(f'blubo.chan {i}', value)
                    except Exception as e:
                        logging.error(f"Error publishing to Adafruit IO: {e}")
                
                tiempo_ultima_publicacion = time.time()

            if is_time_to_close():
                set_servo_angle(92)
            else:
                set_servo_angle(37)

            time.sleep(1)

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()