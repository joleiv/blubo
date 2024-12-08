import pigpio
import sys
import time

class PigpioServoController:
    def __init__(self, servo_pin=13):
        self.servo_pin = servo_pin
        self.pwm = pigpio.pi()
        if not self.pwm.connected:
            print("Error: No se pudo conectar a pigpiod.")
            sys.exit(1)
        
    def set_servo_angle(self, angle):
        # Convierte el ángulo en un pulso PWM
        pulse_width = int((angle / 180.0) * (2500 - 500) + 500)
        self.pwm.set_servo_pulsewidth(self.servo_pin, pulse_width)
        
    def stop_servo(self):
        self.pwm.set_servo_pulsewidth(self.servo_pin, 0)
        time.sleep(1)