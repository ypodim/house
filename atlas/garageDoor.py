import logging
import spidev
import time

from adc import ADC

class GarageDoor(object):
    def __init__(self, gpio):
        self.gpio = gpio
        self.log = logging.getLogger(self.__class__.__name__)
        self.relayPin = 26
        if self.gpio:
            self.gpio.setmode(self.gpio.BCM)
            # self.gpio.setup(self.relayPin, self.gpio.OUT)
        else: 
            self.log.error("GPIO not found")

        self.adc = ADC()
        self.IR_Threshold = 400
        self.lastseen = []
        self.seenLength = 5
        self._isOpen = 0

    def toggle(self):
        print("toggling")
        if not self.gpio:
            return
        self.gpio.setmode(self.gpio.BCM)
        self.gpio.setup(self.relayPin, self.gpio.OUT)
        self.gpio.output(self.relayPin, 1)
        time.sleep(0.1)
        self.gpio.output(self.relayPin, 0)

    @property
    def isOpen(self):
        return "{}".format(self._isOpen)
    
    @property
    def irval(self):
        return "{}".format(self.lastseen[-1])
    
    def pollState(self):
        output = self.adc.getValue(0)
        self._isOpen = int(output < self.IR_Threshold)

        self.lastseen.append(output)
        while len(self.lastseen) > self.seenLength:
            del self.lastseen[0]

if __name__=="__main__":
    import RPi.GPIO as GPIO
    import sys
    from time import sleep
    door = GarageDoor(GPIO)
    # door.setOpen(int(sys.argv[1]))
    #while 1:
    #    door.pollState()
    #    sleep(0.002)


