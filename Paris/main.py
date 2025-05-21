from Paris.street import StreetLampController
import time

# GPIO pin for NeoPixel strip
NEOPIXEL_PIN = 16

# GPIO pins for motion sensors 
MOTION_SENSOR_PINS = [10, 11, 12, 13, 14, 15]

# Create lamp system instance
lamp_system = StreetLampController(
    neopixel_pin=NEOPIXEL_PIN,
    motion_pins=MOTION_SENSOR_PINS,
    num_leds=6,
    color=(255, 255, 255),  
    glow_time=2500,
    neighbor_delay=500,
    use_neighbor_logic=True
)

# Main loop
while True:
    lamp_system.update()
    time.sleep_ms(50)