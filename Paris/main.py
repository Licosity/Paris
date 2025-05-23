
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
NEOPIXEL_PIN = board.D18  # pin 12 
MOTION_PINS = [17, 27, 22, 5, 6, 13]  




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
    finally:
        IndoorF.cleanup()
        GPIO.cleanup()
        print("Programm stopped successfully")





if __name__ == "__main__":
    main()

    
