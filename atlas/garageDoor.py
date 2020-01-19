import logging
import spidev

from adc import ADC

class GarageDoor(object):
    def __init__(self, gpio):
        self.gpio = gpio
        self.log = logging.getLogger(self.__class__.__name__)
        self.relayPin = 26
        if self.gpio:
            self.gpio.setmode(self.gpio.BCM)
            self.gpio.setup(self.relayPin, self.gpio.OUT)
        else: 
            self.log.error("GPIO not found")

        self.adc = ADC()
        self.IR_Threshold = 200
        self.lastseen = []
        self.seenLength = 20
        self._isOpen = 0
    def setOpen(self, state):
        if self.gpio:
            self.gpio.output(self.relayPin, state)

    @property
    def isOpen(self):
        return self._isOpen
    
    def pollState(self):
        output = self.adc.getValue(0)
        self._isOpen = 0
        if output < self.IR_Threshold:
            isOutlier = False
            for previousVal in self.lastseen:
                if abs(output - previousVal) > 30:
                    isOutlier = True
            if not isOutlier:
                self._isOpen = 1

        self.lastseen.append(output)
        while len(self.lastseen) > self.seenLength:
            del self.lastseen[0]

if __name__=="__main__":
    import RPi.GPIO as GPIO
    from time import sleep
    door = GarageDoor(GPIO)
    while 1:
        door.pollState()
        sleep(0.002)