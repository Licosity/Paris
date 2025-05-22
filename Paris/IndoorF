import time
import board
import busio
import digitalio
import adafruit_dht
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from adafruit_mcp3xxx.mcp3008 import MCP3008
import RPi.GPIO as GPIO

led_if_pin=18

class EnvController:
    def __init__(
        self,
        dht_pin=4,
        fan_pin=17,
        ldr_channel=0,
        ldr_threshold=400,
        temp_threshold=28,
        humidity_threshold=60,
        min_fan_on_time=30
    ):
        # --- GPIO Setup ---
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(fan_pin, GPIO.OUT)
        GPIO.output(fan_pin, GPIO.LOW)
        GPIO.setup(led_if_pin, GPIO.OUT)
        GPIO.output(led_if_pin, GPIO.LOW)
        
        self.fan_pin = fan_pin

        # --- DHT22 Sensor ---
        self.dht = adafruit_dht.DHT22(board.D4)  # GPIO 4

        self.temp_threshold = temp_threshold
        self.humidity_threshold = humidity_threshold
        self.min_fan_on_time = min_fan_on_time
        self.last_dht_read = 0
        self.last_fan_on_time = 0
        self.fan_running = False

        self.current_temp = None
        self.current_humidity = None

        # --- MCP3008 for LDR ---
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        self.cs = digitalio.DigitalInOut(board.CE0)
        self.mcp = MCP.MCP3008(self.spi, self.cs)
        self.ldr = AnalogIn(self.mcp, getattr(MCP, f"P{ldr_channel}"))
        self.ldr_threshold = ldr_threshold


    def update(self):
        now = time.monotonic()

        # --- Light control ---
        ldr_value = self.ldr.value
        print(f"[LDR] Value: {ldr_value}")
        if ldr_value < self.ldr_threshold:
            GPIO.output(led_if_pin, GPIO.HIGH)
        else:
            GPIO.output(led_if_pin, GPIO.LOW)

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
        GPIO.output(led_if_pin, GPIO.LOW)
        GPIO.cleanup()
