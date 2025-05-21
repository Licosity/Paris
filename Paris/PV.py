
from  machine import Pin, ADC, PWM
import time

#Definitions NEED ADJUSTMENT!
UPPER_X_SERVO_PIN = 13
UPPER_Y_SERVO_PIN = 12
MIDDLE_X_SERVO_PIN = 14
MIDDLE_Y_SERVO_PIN = 27
LOWER_X_SERVO_PIN = 26
LOWER_Y_SERVO_PIN = 25

UPPER_LED = 34  # ADC-capable pin
RIGHT_LED = 35
LOWER_LED = 32
LEFT_LED = 33
WIND_FLOW_VOLTAGE_PIN = 36
SOLAR_PANELS_VOLTAGE_PIN = 39

#Constants
UPPER_X_OFFSET = 100
UPPER_Y_OFFSET = 90
MIDDLE_X_OFFSET = 90
MIDDLE_Y_OFFSET = 90
LOWER_X_OFFSET = 90
LOWER_Y_OFFSET = 90

TOLERANCE = 200     # Adjusted for 12-bit ADC (0–4095)
WIND_FLOW_TOLERANCE = 200
HISTORY_LENGTH = 60
MOVING_DELAY = 14  # milliseconds

#Helper Functions to control servo
def setup_servo(pin_num):
    pwm = PWM(Pin(pin_num), freq=50)
    return pwm

def write_servo(pwm, angle):
    # Convert 0–180° angle to duty (40–115 for ESP32 PWM)
    duty = int((angle / 180.0) * 75 + 40)
    pwm.duty(duty)

def read_adc(adc):
    return adc.read()

#Setup
upperX = setup_servo(UPPER_X_SERVO_PIN)
upperY = setup_servo(UPPER_Y_SERVO_PIN)
middleX = setup_servo(MIDDLE_X_SERVO_PIN)
middleY = setup_servo(MIDDLE_Y_SERVO_PIN)
lowerX = setup_servo(LOWER_X_SERVO_PIN)
lowerY = setup_servo(LOWER_Y_SERVO_PIN)

adc_upper = ADC(Pin(UPPER_LED))
adc_upper.atten(ADC.ATTN_11DB)
adc_right = ADC(Pin(RIGHT_LED))
adc_right.atten(ADC.ATTN_11DB)
adc_lower = ADC(Pin(LOWER_LED))
adc_lower.atten(ADC.ATTN_11DB)
adc_left = ADC(Pin(LEFT_LED))
adc_left.atten(ADC.ATTN_11DB)
adc_wind = ADC(Pin(WIND_FLOW_VOLTAGE_PIN))
adc_wind.atten(ADC.ATTN_11DB)
adc_solar = ADC(Pin(SOLAR_PANELS_VOLTAGE_PIN))
adc_solar.atten(ADC.ATTN_11DB)

#Variables
x_pos = 0
y_pos = 0
current_x = 0
current_y = 0
previous_x = 0
previous_y = 0
auto_position = True
shadow_safety = False
serial_buffer = ""
voltage_history = []

last_second = time.ticks_ms()
last_twenty = time.ticks_ms()
last_move = time.ticks_ms()

#Main Loop
while True:
    #Serial input for manual control (USB/REPL)
    if serial_buffer == "" and time.ticks_diff(time.ticks_ms(), last_second) >= 500:
        try:
            if input().startswith("§$%&: "):
                line = input()[6:]
                if ',' in line:
                    x_str, y_str = line.split(',')
                    x_pos = int(x_str)
                    y_pos = int(y_str)
                    auto_position = False
                else:
                    auto_position = True
        except Exception:
            pass

    #Every second: store solar voltage
    if time.ticks_diff(time.ticks_ms(), last_second) >= 1000:
        v = read_adc(adc_solar)
        if len(voltage_history) < HISTORY_LENGTH:
            voltage_history.append(v)
        else:
            voltage_history.pop(0)
            voltage_history.append(v)
        last_second = time.ticks_ms()

    #Auto-positioning PV
    if auto_position:
        if read_adc(adc_wind) < WIND_FLOW_TOLERANCE:
            avg = sum(voltage_history) // len(voltage_history) if voltage_history else 0
            if time.ticks_diff(time.ticks_ms(), last_move) >= MOVING_DELAY:
                if (read_adc(adc_right) - read_adc(adc_left)) > TOLERANCE:
                    x_pos += 1
                elif (read_adc(adc_left) - read_adc(adc_right)) > TOLERANCE:
                    x_pos -= 1

                if (read_adc(adc_upper) - read_adc(adc_lower)) > TOLERANCE:
                    y_pos -= 1
                elif (read_adc(adc_lower) - read_adc(adc_upper)) > TOLERANCE:
                    y_pos += 1

                x_pos = max(-90, min(90, x_pos))
                y_pos = max(-90, min(90, y_pos))

                last_move = time.ticks_ms()
        else:
            x_pos, y_pos = 0, 0

    #Every 20s: remember previous position
    if time.ticks_diff(time.ticks_ms(), last_twenty) >= 20000:
        previous_x = x_pos
        previous_y = y_pos
        last_twenty = time.ticks_ms()

    #move to new position
    if time.ticks_diff(time.ticks_ms(), last_move) >= MOVING_DELAY:
        if current_x < x_pos: current_x += 1
        elif current_x > x_pos: current_x -= 1

        if current_y < y_pos: current_y += 1
        elif current_y > y_pos: current_y -= 1

        current_x = max(-90, min(90, current_x))
        current_y = max(-90, min(90, current_y))

        write_servo(upperX, current_x + UPPER_X_OFFSET)
        write_servo(upperY, current_y + UPPER_Y_OFFSET)
        write_servo(middleX, current_x + MIDDLE_X_OFFSET)
        write_servo(middleY, current_y + MIDDLE_Y_OFFSET)
        write_servo(lowerX, current_x + LOWER_X_OFFSET)
        write_servo(lowerY, current_y + LOWER_Y_OFFSET)

        last_move = time.ticks_ms()

    # --- Debugging Output ---
    print("Wind:", read_adc(adc_wind))
    print("X Pos:", x_pos)
    print("Auto Mode:", auto_position)
    print("---------------------------")

    time.sleep_ms(10)
