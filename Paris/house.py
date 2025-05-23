import time
import board
import adafruit_dht
import RPi.GPIO as GPIO

class House:
    def __init__(
        self,
        dht_o_pin=13,
        motion_o_pin=15,
        infra_o_pin=17,
        dht_u_pin=14,
        motion_u_pin=16,
        infra_u_pin=18,
        min_temp=17,
        run_time=30
    ):
        GPIO.setmode(GPIO.BCM)
        
        # Save pins
        self.dht_o_pin = dht_o_pin
        self.motion_o_pin = motion_o_pin
        self.infra_o_pin = infra_o_pin
        self.dht_u_pin = dht_u_pin
        self.motion_u_pin = motion_u_pin
        self.infra_u_pin = infra_u_pin
        
        # Setup GPIO
        GPIO.setup(self.motion_o_pin, GPIO.IN)
        GPIO.setup(self.motion_u_pin, GPIO.IN)
        GPIO.setup(self.infra_o_pin, GPIO.OUT)
        GPIO.output(self.infra_o_pin, GPIO.LOW)
        GPIO.setup(self.infra_u_pin, GPIO.OUT)
        GPIO.output(self.infra_u_pin, GPIO.LOW)

        # Setup DHT22 sensors
        self.dht_o = adafruit_dht.DHT22(getattr(board, f"D{self.dht_o_pin}"))
        self.dht_u = adafruit_dht.DHT22(getattr(board, f"D{self.dht_u_pin}"))

        # State
        self.last_activation_o = 0
        self.last_activation_u = 0
        self.min_temp = min_temp
        self.run_time = run_time

    def _check_zone(self, dht_sensor, motion_pin, infra_pin, last_activation_time):
        try:
            temp = dht_sensor.temperature
            motion = GPIO.input(motion_pin)
            now = time.time()

            if temp is not None and temp < self.min_temp and motion:
                GPIO.output(infra_pin, GPIO.HIGH)
                return now  # Update activation time
            elif now - last_activation_time >= self.run_time:
                GPIO.output(infra_pin, GPIO.LOW)
        except RuntimeError:
            pass
        return last_activation_time

    def update(self):
        self.last_activation_o = self._check_zone(
            self.dht_o, self.motion_o_pin, self.infra_o_pin, self.last_activation_o
        )
        self.last_activation_u = self._check_zone(
            self.dht_u, self.motion_u_pin, self.infra_u_pin, self.last_activation_u
        )
