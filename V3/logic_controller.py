import time
import logging
import sys
from datetime import datetime

class LogicController:
    """
    Controla la lógica principal de la aplicación: leer datos, escribir en archivos,
    controlar el servo según la hora, y responder a errores.
    """
    def __init__(self, config, servo_controller, ads_reader, file_writer, servo_pattern_player):
        self.config = config
        self.servo = servo_controller
        self.ads_reader = ads_reader
        self.file_writer = file_writer
        self.servo_pattern_player = servo_pattern_player

        self.time_to_close_start = self.config.get("time_to_close_start", "08:00:00")
        self.time_to_close_end = self.config.get("time_to_close_end", "17:30:00")

        # Valores de ángulo desde el config
        self.angle_closed = self.config.get("angle_closed", 92)
        self.angle_open = self.config.get("angle_open", 37)

    def is_time_to_close(self):
        now = datetime.now().time()
        start_time = datetime.strptime(self.time_to_close_start, "%H:%M:%S").time()
        end_time = datetime.strptime(self.time_to_close_end, "%H:%M:%S").time()
        return start_time <= now <= end_time

    def run(self):
        # Al iniciar, podemos reproducir un patrón (por ejemplo "device_on")
        self.servo_pattern_player.play("device_on")

        while True:
            try:
                timestamp = time.time()
                values, voltages = self.ads_reader.read_values()

                # Impresión de datos
                print("\t\t\tCH01\tCH02\tCH03")
                print(f'{time.strftime("[%Y-%m-%d %H:%M:%S]")}\t{voltages[0]}\t{voltages[1]}\t{voltages[2]}')

                # Escritura en archivos
                self.file_writer.write_data(timestamp, values)

                # Control del servo según la hora usando valores del config
                if self.is_time_to_close():
                    self.servo.set_servo_angle(self.angle_closed)
                else:
                    self.servo.set_servo_angle(self.angle_open)

                time.sleep(1)

            except Exception as e:
                logging.error(f"An error occurred: {e}")
                # Ejemplo: reproducir patrón de error_1
                self.servo_pattern_player.play("error_1")

    def stop(self):
        """
        Llamado cuando se recibe SIGINT u otra señal para terminar.
        """
        self.servo.stop_servo()
        sys.exit(0)
