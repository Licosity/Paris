import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
import sys

class House:
    def __init__(
        self,
        dht_o_pin=27,
        motion_o_pin=23,
        infra_o_pin=25,
        dht_u_pin=17,
        motion_u_pin=22,
        infra_u_pin=24,
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

        try:
            print(f"Initializing DHT22 sensor on GPIO {self.dht_o_pin}")
            self.dht_o = adafruit_dht.DHT22(self._get_board_pin(self.dht_o_pin))
            print(f"Initializing DHT22 sensor on GPIO {self.dht_u_pin}")
            self.dht_u = adafruit_dht.DHT22(self._get_board_pin(self.dht_u_pin))
        except Exception as e:
            print(f"Failed to initialize DHT22 sensors: {e}")
            sys.exit(1)

        # State
        self.last_activation_o = 0
        self.last_activation_u = 0
        self.min_temp = min_temp
        self.run_time = run_time

    def _get_board_pin(self, gpio_num):
        try:
            return getattr(board, f"D{gpio_num}")
        except AttributeError:
            print(f"[ERROR] board.D{gpio_num} does not exist.")
            print("Use GPIO pin numbers correctly. Example: GPIO4 = board.D4")
            sys.exit(1)

    def _check_zone(self, dht_sensor, motion_pin, infra_pin, last_activation_time, label):
        try:
            temp = dht_sensor.temperature
            humidity = dht_sensor.humidity
            motion = GPIO.input(motion_pin)
            now = time.time()

            print(f"[{label}] Temp: {temp}°C, Humidity: {humidity}%, Motion: {motion}")

            if temp is not None and temp < self.min_temp and motion:
                GPIO.output(infra_pin, GPIO.HIGH)
                print(f"[{label}] 🟥 Infrared ON")
                return now
            elif now - last_activation_time >= self.run_time:
                GPIO.output(infra_pin, GPIO.LOW)
                print(f"[{label}] 🟩 Infrared OFF (Timeout)")

        except RuntimeError as e:
            print(f"[{label}] RuntimeError: {e}")
        except Exception as e:
            print(f"[{label}] Unexpected error: {e}")
        return last_activation_time

    def update(self):
        self.last_activation_o = self._check_zone(
            self.dht_o, self.motion_o_pin, self.infra_o_pin, self.last_activation_o, label="Outside"
        )
        self.last_activation_u = self._check_zone(
            self.dht_u, self.motion_u_pin, self.infra_u_pin, self.last_activation_u, label="Inside"
        )

# Main
house = House()
try:
    print("🏠 House monitoring started...")
    while True:
        house.update()
        time.sleep(0.5)
except KeyboardInterrupt:
    print("🛑 Cleaning up program...")
    GPIO.cleanup()
