#!/usr/bin/python3

import serial
import time

class Bridge(object):
    def __init__(self):
        self.ser = serial.Serial('/dev/serial0', 9600)
        self.running = True
    def run(self):
        while self.running:
            # self.ser.write(b'%c' % 50)
            line = self.ser.readline().strip()
            # print(len(line))
            # adc0 = line[0]
            # adc1 = line[1]
            # adc2 = line[2]
            # adc3 = line[3]
            # print(adc0, adc1, adc2, adc3)
            print(line)
    def water(self):
        for i in range(8):
            relayOn  = i + 40
            relayOff = i + 50
            
            self.ser.write(b'%c' % relayOn)
            time.sleep(660)
            self.ser.write(b'%c' % relayOff)
            time.sleep(1)

if __name__=="__main__":
    print("starting")
    b = Bridge()
    try:
        b.run()
    except KeyboardInterrupt:
        b.running = False

