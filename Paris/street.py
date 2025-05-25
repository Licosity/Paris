import time
import board
import rpi_ws281x
import neopixel
import RPi.GPIO as GPIO


#street constants
GLOW_TIME = 3  # seconds
DELAY_TIME = 0.3  # seconds
WHITE = (255, 255, 255)
NEOPIXEL_PIN = 4  # actual pin 7
MOTION_PINS = [17, 12, 27, 22, 23, 24]  # actual pin 11, 12, 13, 15, 16, 18


class StreetLampController:
    def __init__(self, NEOPIXEL_PIN, MOTION_PIN, color=WHITE, use_neighbor_logic=True):
        self.num_lamps = len(MOTION_PIN)
        self.color = color
        self.motion_pins = MOTION_PIN
        self.use_neighbor_logic = use_neighbor_logic

        # Setup motion sensors
        GPIO.setmode(GPIO.BCM)
        for pin in MOTION_PIN:
            GPIO.setup(pin, GPIO.IN)

        # Setup NeoPixel strip
        self.strip = neopixel.NeoPixel(NEOPIXEL_PIN, self.num_lamps, auto_write=False)

        # State tracking
        self.motion_states = [False] * self.num_lamps
        self.timer_on = [0.0] * self.num_lamps
        self.neighbor_triggers = [False] * self.num_lamps
        self.neighbor_timer = [0.0] * self.num_lamps

    def update(self):
        current_time = time.monotonic()

        # 1. Check motion sensors
        for i, pin in enumerate(self.motion_pins):
            self.motion_states[i] = GPIO.input(pin) == GPIO.HIGH

        # 2. Handle direct motion triggers
        for i in range(self.num_lamps):
            if self.motion_states[i]:
                self.timer_on[i] = current_time
                self.strip[i] = self.color
            else:
                if current_time - self.timer_on[i] > GLOW_TIME:
                    self.strip[i] = (0, 0, 0)

        # 3. Neighbor logic
        if self.use_neighbor_logic:
            
            for i in range(self.num_lamps):
                if not self.motion_states[i]:
                    left = i - 1 if i > 0 else 0
                    right = i + 1 if i < self.num_lamps - 1 else self.num_lamps - 1
                    if self.motion_states[left] or self.motion_states[right]:
                        if not self.neighbor_triggers[i]:
                            self.neighbor_triggers[i] = True
                            self.neighbor_timer[i] = current_time

                if self.neighbor_triggers[i] and current_time - self.neighbor_timer[i] > DELAY_TIME:
                    self.strip[i] = self.color
                    self.timer_on[i] = current_time
                    self.neighbor_triggers[i] = False

        # 4. Push to strip
        self.strip.show()

street  = StreetLampController()
#test
try:
    while True:
        street.update()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Cleaning up program...")
    GPIO.cleanup()
