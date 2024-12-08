import time
import sys
import logging
import signal
from datetime import datetime
import subprocess

from servo_controller import PigpioServoController
from ads_reader import ADSReader
from file_writer import FileWriter

class Application:
    TIME_TO_CLOSE_START = "08:00:00"
    TIME_TO_CLOSE_END = "17:30:00"

    def __init__(self):
        # Inicializar logging
        logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        # Verificar pigpiod
        if not self.check_pigpiod():
            print("'pigpiod' está desactivado")
            sys.exit(1)
        
        self.servo = PigpioServoController(servo_pin=13)
        self.ads_reader = ADSReader()
        self.file_writer = FileWriter()

        signal.signal(signal.SIGINT, self.signal_handler)

    def check_pigpiod(self):
        try:
            subprocess.check_output(["pidof", "pigpiod"])
            return True
        except subprocess.CalledProcessError:
            return False

    def signal_handler(self, sig, frame):
        print('\nKill command received from keyboard - script exiting')
        self.servo.stop_servo()
        sys.exit(0)

    def is_time_to_close(self):
        now = datetime.now().time()
        start_time = datetime.strptime(self.TIME_TO_CLOSE_START, "%H:%M:%S").time()
        end_time = datetime.strptime(self.TIME_TO_CLOSE_END, "%H:%M:%S").time()
        return start_time <= now <= end_time

    def run(self):
        while True:
            try:
                timestamp = time.time()
                values, voltages = self.ads_reader.read_values()

                # Impresión de datos
                print("\t\t\tCH01\tCH02\tCH03")
                print(f'{time.strftime("[%Y-%m-%d %H:%M:%S]")}\t{voltages[0]}\t{voltages[1]}\t{voltages[2]}')

                # Escritura en archivos
                self.file_writer.write_data(timestamp, values)

                # Control del servo según la hora
                if self.is_time_to_close():
                    self.servo.set_servo_angle(92)
                else:
                    self.servo.set_servo_angle(37)

                time.sleep(1)

            except Exception as e:
                logging.error(f"An error occurred: {e}")