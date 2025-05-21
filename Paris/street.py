import time
import board
import rpi_ws281x
import neopixel
import RPi.GPIO as GPIO

# Constants
GLOW_TIME = 5  # seconds
DELAY_TIME = 0.5  # seconds
NUM_LAMPS = 6
WHITE = (255, 255, 255)


class StreetLampController:
    def __init__(self, neopixel_pin, motion_pins, color=WHITE, use_neighbor_logic=True):
        self.num_lamps = len(motion_pins)
        self.color = color
        self.motion_pins = motion_pins
        self.use_neighbor_logic = use_neighbor_logic

        # Setup motion sensors
        GPIO.setmode(GPIO.BCM)
        for pin in motion_pins:
            GPIO.setup(pin, GPIO.IN)

        # Setup NeoPixel strip
        self.strip = neopixel.NeoPixel(neopixel_pin, self.num_lamps, auto_write=False)

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
