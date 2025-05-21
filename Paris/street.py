
import machine
import neopixel
import time

#pin values in main.py 

class StreetLampController:
    # config lamps
    def __init__(self, neopixel_pin, motion_pins, num_leds=6, color=(255, 255, 255),
                 glow_time=5000, neighbor_delay=500, use_neighbor_logic=True):
        self.num_leds = num_leds
        self.color = color
        self.glow_time = glow_time
        self.neighbor_delay = neighbor_delay
        self.use_neighbor_logic = use_neighbor_logic

        self.strip = neopixel.NeoPixel(machine.Pin(neopixel_pin), num_leds)
        self.motion_sensors = [machine.Pin(pin, machine.Pin.IN) for pin in motion_pins]

        self.glow_until = [0] * num_leds
        self.neighbor_trigger_time = [0] * num_leds
        self.neighbor_triggered = [False] * num_leds

    def _set_led(self, index, color):
        self.strip[index] = color

    def _clear_led(self, index):
        self._set_led(index, (0, 0, 0))

    # config motion sensors 
    def _handle_motion(self, now, motion_flags):
        for i in range(self.num_leds):
            if motion_flags[i]:
                self._set_led(i, self.color)
                self.glow_until[i] = now + self.glow_time
    
    # config react to neighbor 
    def _handle_neighbors(self, now, motion_flags):
        for i in range(self.num_leds):
            if not motion_flags[i]:
                left = motion_flags[i - 1] if i > 0 else False
                right = motion_flags[i + 1] if i < self.num_leds - 1 else False
                if left or right:
                    self.neighbor_trigger_time[i] = now + self.neighbor_delay
                    self.neighbor_triggered[i] = True

    # config updating led to current status
    def _update_leds(self, now):
        for i in range(self.num_leds):
            if self.neighbor_triggered[i] and now >= self.neighbor_trigger_time[i]:
                self._set_led(i, self.color)
                self.glow_until[i] = now + self.glow_time
                self.neighbor_triggered[i] = False

            if now > self.glow_until[i]:
                self._clear_led(i)

        self.strip.write() # writes the new config to the leds

    def update(self):
        now = time.ticks_ms()
        motion_flags = [sensor.value() for sensor in self.motion_sensors] # reading all sensors

        self._handle_motion(now, motion_flags) # trigges led if motion is detected

        if self.use_neighbor_logic:
            self._handle_neighbors(now, motion_flags) # checking for neighbors Leds

        self._update_leds(now) 

