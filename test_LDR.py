mport time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
# Den I2C-Bus erstellen
i2c = busio.I2C(board.SCL, board.SDA)
# Erstellen des ADC-Objekts über den I2C-Bus
ads = ADS.ADS1115(i2c)
# Single-Ended-Eingang auf Kanälen erstellen
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)
while True:
print("Kanal 0: ","{:>5}\t{:>5.3f}".format
(chan0.value, chan0.voltage))
print("Kanal 1: ","{:>5}\t{:>5.3f}".format
(chan1.value, chan1.voltage))
print("Kanal 2: ","{:>5}\t{:>5.3f}".format
(chan2.value, chan2.voltage))
print("Kanal 3: ","{:>5}\t{:>5.3f}".format
(chan3.value, chan3.voltage))
print("----")
time.sleep(1)
