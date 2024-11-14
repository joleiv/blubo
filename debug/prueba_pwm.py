import pigpio
import time

# Inicializar pigpio
pi = pigpio.pi()

# Verificar si se pudo conectar con el demonio pigpiod
if not pi.connected:
    print("No se pudo conectar con pigpiod. Asegúrate de que está en ejecución.")
    exit()

SERVO_PIN = 13  # Cambia este valor al pin GPIO que estés usando

# Configuración de los límites de pulso para el servomotor (en microsegundos)
MIN_PULSE_WIDTH = 500
MAX_PULSE_WIDTH = 2500

def set_servo_angle(angle):
    # Convertir el ángulo (0 a 180 grados) a pulso
    pulse_width = int((angle / 180.0) * (MAX_PULSE_WIDTH - MIN_PULSE_WIDTH) + MIN_PULSE_WIDTH)
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
    print(f"Ángulo establecido a {angle} grados (ancho de pulso: {pulse_width}us)")

try:
    # Prueba moviendo el servo a diferentes ángulos
  #  while True:
   #     for angle in range(0, 181, 30):
    #        set_servo_angle(angle)
     #       time.sleep(1)
      #  for angle in range(180, -1, -30):
       #     set_servo_angle(angle)
        #    time.sleep(1)
        angle = 37 #(abierto)
        #angle = 95
        set_servo_angle(angle)
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    # Detener el servo y limpiar
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()
    print("Script terminado y recursos liberados.")