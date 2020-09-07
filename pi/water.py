#!/usr/bin/python3

import asyncio
import serial
import time

class ArduinoSerial():
    def __init__(self, loop, clb=None):
        self.loop = loop
        self.clb = clb
        self.s = serial.Serial('/dev/serial0', 57600)
        self.data_recv = ""
        self.startedRunningAt = 0
    def reader(self):
        data = self.s.read().decode("ascii")
        self.data_recv += data
        if data[-1] == '\n':
            if self.clb:
                self.loop.call_soon(self.clb, self.data_recv.strip())
            else:
                self.loop.call_soon(self.readclb, self.data_recv.strip())
            self.data_recv = ""
    def write(self, data):
        self.s.write(data)

    def water(self, onValve, offValve=None):
        # times = [7, 10, 14, 6, 11, 5]
        times = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]

        if offValve != None:
            data = '%c' % (offValve + 50)
            self.s.write(data.encode())
            elapsed = 1.0 * (time.time() - self.startedRunningAt)/60
            print("valve %s run for %s mins\n" % (offValve, elapsed))

        if onValve >= len(times):
            return

        data = '%c' % (onValve + 40)
        self.s.write(data.encode())
        self.startedRunningAt = time.time()

        self.loop.call_later(times[onValve]*60, self.water, onValve+1, onValve)

    def allOff(self):
        for i in range(8):
            relayOff = i + 50
            self.s.write(b'%c' % relayOff)

    def set(self, relay, state):
        relay += 40
        if state == False:
            relay += 10
        self.s.write(b'%c' % relay)

    def toggle(self, relay):
        self.s.write(b'%c' % (relay+50))
        time.sleep(0.2)
        self.s.write(b'%c' % (relay+40))
        time.sleep(0.2)
        self.s.write(b'%c' % (relay+50))

    def readclb(self, data):
        if data.startswith("relay"):
            print(data)
        elif data.startswith("inactivity"):
            print(data)
        else:
            pass

    def poll(self):
        self.s.write(b'%c' % 70)
        self.loop.call_later(5, self.poll)

def main3():
    loop = asyncio.get_event_loop()
    ars = ArduinoSerial(loop)
    
    loop.add_reader(ars.s, ars.reader)
    # loop.call_soon(ars.water, 4)
    loop.call_soon(ars.poll)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        ars.allOff()
        loop.close()


if __name__=="__main__":
    main3()

