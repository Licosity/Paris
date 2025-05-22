import time
import threading

# For Raspberry Pi GPIO handling
import RPi.GPIO as GPIO

class SolarTracker:
    def __init__(self):
        # GPIO Mode
        GPIO.setmode(GPIO.BCM)

        # Servo pins (use actual PWM-capable GPIO pins)
        self.servo_pins = {
            'upper_x': 13,
            'upper_y': 12,
            'middle_x': 14,
            'middle_y': 27,
            'lower_x': 26,
            'lower_y': 25
        }

        # Light sensor pins (use MCP3008 via SPI or I2C ADC chip if analog input needed)
        # Here we assume a function to read analog values, to be implemented separately
        self.sensor_labels = ['upper', 'right', 'lower', 'left', 'wind', 'solar']

        # Servo Offsets
        self.offsets = {
            'upper_x': 100,
            'upper_y': 90,
            'middle_x': 90,
            'middle_y': 90,
            'lower_x': 90,
            'lower_y': 90
        }

        # Constants
        self.TOLERANCE = 200
        self.WIND_FLOW_TOLERANCE = 200
        self.HISTORY_LENGTH = 60
        self.MOVING_DELAY = 0.014  # seconds

        # Servo setup
        self.servos = self.setup_servos()

        # State variables
        self.x_pos = 0
        self.y_pos = 0
        self.current_x = 0
        self.current_y = 0
        self.previous_x = 0
        self.previous_y = 0
        self.auto_position = True
        self.shadow_safety = False
        self.voltage_history = []

        # Timers
        self.last_second = time.time()
        self.last_twenty = time.time()
        self.last_move = time.time()

    def setup_servos(self):
        servos = {}
        for label, pin in self.servo_pins.items():
            GPIO.setup(pin, GPIO.OUT)
            pwm = GPIO.PWM(pin, 50)
            pwm.start(0)
            servos[label] = pwm
        return servos

    def write_servo(self, label, angle):
        duty = (angle / 18.0) + 2
        self.servos[label].ChangeDutyCycle(duty)

    def read_adc(self, label):
        # Placeholder: should read from MCP3008 or similar
        return 0

    def update_voltage_history(self):
        v = self.read_adc('solar')
        if len(self.voltage_history) < self.HISTORY_LENGTH:
            self.voltage_history.append(v)
        else:
            self.voltage_history.pop(0)
            self.voltage_history.append(v)

    def auto_position_logic(self):
        if self.read_adc('wind') < self.WIND_FLOW_TOLERANCE:
            if len(self.voltage_history):
                avg = sum(self.voltage_history) // len(self.voltage_history)

            if time.time() - self.last_move >= self.MOVING_DELAY:
                if self.read_adc('right') - self.read_adc('left') > self.TOLERANCE:
                    self.x_pos += 1
                elif self.read_adc('left') - self.read_adc('right') > self.TOLERANCE:
                    self.x_pos -= 1

                if self.read_adc('upper') - self.read_adc('lower') > self.TOLERANCE:
                    self.y_pos -= 1
                elif self.read_adc('lower') - self.read_adc('upper') > self.TOLERANCE:
                    self.y_pos += 1

                self.x_pos = max(-90, min(90, self.x_pos))
                self.y_pos = max(-90, min(90, self.y_pos))

                self.last_move = time.time()
        else:
            self.x_pos = 0
            self.y_pos = 0

    def move_servos(self):
        if time.time() - self.last_move >= self.MOVING_DELAY:
            if self.current_x < self.x_pos: self.current_x += 1
            elif self.current_x > self.x_pos: self.current_x -= 1

            if self.current_y < self.y_pos: self.current_y += 1
            elif self.current_y > self.y_pos: self.current_y -= 1

            self.current_x = max(-90, min(90, self.current_x))
            self.current_y = max(-90, min(90, self.current_y))

            for label in ['upper', 'middle', 'lower']:
                self.write_servo(f'{label}_x', self.current_x + self.offsets[f'{label}_x'])
                self.write_servo(f'{label}_y', self.current_y + self.offsets[f'{label}_y'])

            self.last_move = time.time()

    def update_previous_position(self):
        if time.time() - self.last_twenty >= 20:
            self.previous_x = self.x_pos
            self.previous_y = self.y_pos
            self.last_twenty = time.time()

    def run(self):
        try:
            while True:
                self.update_voltage_history()
                if self.auto_position:
                    self.auto_position_logic()
                self.update_previous_position()
                self.move_servos()

                # Debug
                print("Wind:", self.read_adc('wind'))
                print("X Pos:", self.x_pos)
                print("Auto Mode:", self.auto_position)
                print("---------------------------")

                time.sleep(0.01)
        except KeyboardInterrupt:
            for pwm in self.servos.values():
                pwm.stop()
            GPIO.cleanup()


