from logger import Logger

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    GPIO = None
    print("Could not load GPIO. Not running on Rasp?")


class Relay(object):
    def __init__(self, pin, name, state=0):
        self.pin = pin
        self.name = name
        self.state = state
        GPIO.setup(self.pin, GPIO.OUT)
    def set(self, state):
        self.state = state
        GPIO.output(self.pin, self.state)
    def toggle(self):
        newState = (not self.state)
        self.set(newState)
    def isOn(self):
        return (self.state)


class Relays(object):
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.log = Logger(__class__.__name__)
        self.relayPins = {}
        self.garage = Relay(26, "garage")
        self.water = Relay(13, "front lawn")
        self.water2 = Relay(19, "water2")
        self.water3 = Relay(6, "water3")
        

if __name__=="__main__":
    import RPi.GPIO as GPIO
    import sys


