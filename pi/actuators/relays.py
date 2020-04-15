import logging
import time

try:
    from adc import ADC
    import RPi.GPIO as GPIO 
except:
    ADC = None
    GPIO = None
    logging.error("Could not load GPIO. Not running on Rasp?")

class Relay(object):
    def __init__(self):
        self.gpio = GPIO
        self.log = logging.getLogger(self.__class__.__name__)
        self.relayPin = 26
        if self.gpio:
            self.gpio.setmode(self.gpio.BCM)
            # self.gpio.setup(self.relayPin, self.gpio.OUT)
        else: 
            self.log.error("GPIO not found")

    def toggle(self):
        print("toggling garage door")
        if not self.gpio:
            return
        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setup(self.relayPin, self.gpio.OUT)
        self.gpio.output(self.relayPin, 1)
        time.sleep(0.1)
        self.gpio.output(self.relayPin, 0)
        print("done.")

if __name__=="__main__":
    import RPi.GPIO as GPIO
    import sys


