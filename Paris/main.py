
import board
import time
import rpi_ws281x
import neopixel
import RPi.GPIO as GPIO

from street import StreetLampController
from env_controller import EnvController


#street constants
GLOW_TIME = 3  # seconds
DELAY_TIME = 0.3  # seconds
NUM_LAMPS = 6
WHITE = (255, 255, 255)
NEOPIXEL_PIN = board.D18  # pin 12 
MOTION_SENSOR_PINS = [17, 27, 22, 5, 6, 13]  


def main():
    controller = EnvController(
       
        dht_pin=4,
        fan_pin=17,
        led_pin=18,
        num_leds=8,
        ldr_channel=0 
    )


try:
    while True:
        controller.update()
        lamp_system.update()
        time.sleep(0.05)
except KeyboardInterrupt: # ctrl C to stop programm 
    print("Cleaning up GPIO...")
    controller.cleanup()
    GPIO.cleanup()



if __name__ == "__main__":
    main()

    
#PV:
# from solar_tracker import SolarTracker
# tracker = SolarTracker()
# threading.Thread(target=tracker.run).start()
