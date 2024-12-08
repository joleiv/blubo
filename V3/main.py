from config_manager import ConfigManager
from servo_controller import PigpioServoController
from ads_reader import ADSReader
from file_writer import FileWriter
from servo_pattern_player import ServoPatternPlayer
from logic_controller import LogicController
from rtc import RTC  # Asumiendo que tienes esta clase para la sincronización

def main():
    # Configurar logging, verificar pigpiod, etc.
    # ...

    config = ConfigManager()
    servo = PigpioServoController(servo_pin=config.get("servo_pin", 13))
    ads_reader = ADSReader()

    # Instanciar RTC y sincronizar hora si es necesario
    rtc = RTC()
    rtc.sync_system_time()  # Ajusta la hora del sistema con el RTC
    last_rtc_update = rtc.read_current_time()  # Leer la hora actual del RTC para el header

    file_writer = FileWriter(config, last_rtc_update)
    error_patterns = config.get("error_patterns", {})
    servo_pattern_player = ServoPatternPlayer(servo, error_patterns)

    logic = LogicController(config, servo, ads_reader, file_writer, servo_pattern_player)
    # Manejo de señal SIGINT
    # ...

    logic.run()

if __name__ == "__main__":
    main()