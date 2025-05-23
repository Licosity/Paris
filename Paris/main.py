
import board
import time
import rpi_ws281x
import neopixel
import RPi.GPIO as GPIO

from street import StreetLampController
from IndoorF import EnvController
from house import House

#street constants
GLOW_TIME = 3  # seconds
DELAY_TIME = 0.3  # seconds
WHITE = (255, 255, 255)
NEOPIXEL_PIN = 4  # actual pin 7
MOTION_PINS = [17, 12, 27, 22, 23, 24]  # actual pin 11, 12, 13, 15, 16, 18




def main():
    house = House()
    IndoorF = EnvController()
    street = StreetLampController()

    try:
        while True:
            IndoorF.update()
            street.update()
            house.update()
            time.sleep(0.08)
    except KeyboardInterrupt: # ctrl C to stop programm 
        print("Cleaning up program...")
        IndoorF.cleanup()
        GPIO.cleanup()





if __name__ == "__main__":
    main()

    
