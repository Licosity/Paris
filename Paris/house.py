import time
import board
import adafruit_dht
import RPi.GPIO as GPIO

class House:
    def __init__(
        self,
        dht_o_pin=13, # actual pin 33
        motion_o_pin=5, # actual pin 29
        infra_o_pin=19, # actual pin 35
        dht_u_pin=12, # actual pin 32
        motion_u_pin=6, # actual pin 31
        infra_u_pin=26, # actual pin 37
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

    def _check_zone(self, dht_sensor, motion_pin, infra_pin, last_activation_time):
        try:
            temp = dht_sensor.temperature
            motion = GPIO.input(motion_pin)
            now = time.time()
            print(f"[{label}] Temp: {temp}°C, Humidity: {humidity}%, Motion: {motion}")

            if temp is not None and temp < self.min_temp and motion:
                GPIO.output(infra_pin, GPIO.HIGH)
                return now 
            
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

house = House()
#test
try:
    while True:
        house.update()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Cleaning up program...")
    GPIO.cleanup()
