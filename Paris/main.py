
import board
import time
from street import StreetLampController

NEOPIXEL_PIN = board.D18  # GPIO18 (physical pin 12) 
MOTION_SENSOR_PINS = [17, 27, 22, 5, 6, 13]  

lamp_system = StreetLampController(
    neopixel_pin=NEOPIXEL_PIN,
    motion_pins=MOTION_SENSOR_PINS,
    color=(255, 255, 255),  
    use_neighbor_logic=True
)

try:
    while True:
        lamp_system.update()
        time.sleep(0.05)
except KeyboardInterrupt: # ctrl C to stop programm properly
    print("Cleaning up GPIO...")
    import RPi.GPIO as GPIO
    GPIO.cleanup()
