import time
import board
import busio
import digitalio
import adafruit_dht
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO


LED_IF_PIN = 20, # actual pin 38
fan_pin=12, # actual pin 36
class EnvController:
    def __init__(
        self,
        dht_pin=6, # actual pin 32
        fan_pin=12, # actual pin 36
        ldr_channel=0,
        ldr_threshold=100,
        temp_threshold=0.5,
        humidity_threshold=60,
        min_fan_on_time=30,
    ):
        # --- GPIO Setup ---
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(fan_pin, GPIO.OUT)
        GPIO.output(fan_pin, GPIO.LOW)
        GPIO.setup(LED_IF_PIN, GPIO.OUT)
        GPIO.output(LED_IF_PIN, GPIO.LOW)
        
        self.fan_pin = fan_pin
        self.LED_IF_PIN  = LED_IF_PIN
        # --- DHT22 Sensor ---
        self.dht = adafruit_dht.DHT22(board.D6)  # actual pin 32

        self.temp_threshold = temp_threshold
        self.humidity_threshold = humidity_threshold
        self.min_fan_on_time = min_fan_on_time
        self.last_dht_read = 0
        self.last_fan_on_time = 0
        self.fan_running = False

        self.current_temp = None
        self.current_humidity = None

        # --- ADS1115 for LDR ---
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.ldr = AnalogIn(self.ads, getattr(ADS, f"P{ldr_channel}"))
        self.ldr_threshold = ldr_threshold


    def update(self):
        now = time.monotonic()

        # --- Light control ---
        ldr_voltage = self.ldr.voltage
        print(f"[LDR] Voltage: {ldr_voltage:.3f} V")
        if ldr_voltage < self.ldr_threshold:
            GPIO.output(self.LED_IF_PIN, GPIO.HIGH)
        else:
            GPIO.output(self.LED_IF_PIN, GPIO.LOW)


        # --- Climate control ---
        if now - self.last_dht_read >= 3:
            try:
                self.current_temp = self.dht.temperature
                self.current_humidity = self.dht.humidity
                print(f"[DHT22] Temp: {self.current_temp}°C, Humidity: {self.current_humidity}%")
            except RuntimeError as e:
                print("[DHT22] Read error:", e)
            self.last_dht_read = now

        # Fan logic
        if (
            (self.current_temp and self.current_temp > self.temp_threshold)
            or (self.current_humidity and self.current_humidity > self.humidity_threshold)
        ):
            if not self.fan_running:
                GPIO.output(self.fan_pin, GPIO.HIGH)
                self.fan_running = True
                self.last_fan_on_time = now
                print("[Fan] ON")

        if self.fan_running and now - self.last_fan_on_time >= self.min_fan_on_time:
            GPIO.output(self.fan_pin, GPIO.LOW)
            self.fan_running = False
            print("[Fan] OFF")

    def cleanup(self):
        GPIO.output(self.fan_pin, GPIO.LOW)
        GPIO.output(LED_IF_PIN, GPIO.LOW)
        GPIO.cleanup()

IndoorF = EnvController()
#test


try:
    while True:
        IndoorF.update()

        time.sleep(1.1)

except KeyboardInterrupt:
    print("Cleaning up program...")
    IndoorF.cleanup()
