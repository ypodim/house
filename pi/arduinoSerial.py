#!/usr/bin/python3

import asyncio
import serial
import time
from logger import Logger


class ArduinoSerial():
    def __init__(self, loop, clb=None):
        self.loop = loop
        self.clb = clb
        self.s = serial.Serial('/dev/serial0', 57600)
        self.data_recv = ""
        self.startedRunningAt = 0
        self._adc = []
        self.relay_state = [0,0,0,0,0,0,0,0]
        self.log = Logger(__class__.__name__)
    def reader(self):
        data = self.s.read()
        try:
            data = data.decode("ascii")
        except:
            # self.log.log("error decoding %s" % [ord(x) for x in data])
            self.log.log("error decoding %s" % data)
            return

        self.data_recv += data
        if data[-1] == '\n':
            self.loop.call_soon(self.readclb, self.data_recv.strip())
            self.data_recv = ""
    def write(self, data):
        datastr = "%s" % data
        self.s.write(datastr.encode())

    def water(self, onValve, offValve=None):
        # times = [3, 3, 3, 3, 3, 3]
        times = [0.03, 0.03, 0.03]

        if offValve != None:
            self.turnOff(offValve)
            elapsed = 1.0 * (time.time() - self.startedRunningAt)/60
            # print("valve %s run for %s mins\n" % (offValve, elapsed))

        if onValve >= len(times):
            self.loop.stop()
            return
            
        self.turnOn(onValve)
        self.startedRunningAt = time.time()

        self.loop.call_later(times[onValve]*60, self.water, onValve+1, onValve)

    def allOff(self):
        for i in range(8):
            relayOff = i + 50
            self.s.write(b'%c' % relayOff)

    def set(self, relay, state):
        relay += 40
        if not state:
            relay += 10
        return self.s.write(b'%c' % relay)

    def turnOff(self, relay):
        self.log.log("turning off %s" % relay)
        return self.set(relay, False)
    def turnOn(self, relay):
        self.log.log("turning on %s" % relay)
        return self.set(relay, True)

    def get(self):
        return self.relay_state

    def readclb(self, data):
        if data.startswith("relay"):
            if self.clb:
                self.clb(data)
            self.relay_state = [int(x) for x in data.split(':')[1:]]
        elif data.startswith("inactivity"):
            print(data)
        else:
            if data:
                try:
                    self._adc = [int(x) for x in data.split(',')]
                except:
                    print(data)

    def poll(self):
        POLL_CMD = 70
        self.s.write(b'%c' % POLL_CMD)
        self.loop.call_later(3, self.poll)

    def __str__(self):
        return "arduinoserial"
    def __getattr__(self, attr):
        if attr == "value":
            return {"adc": self._adc, "relays": self.relay_state}
        else:
            return "unknown attr: %s" % attr

def main3():
    loop = asyncio.get_event_loop()
    ars = ArduinoSerial(loop)
    
    loop.add_reader(ars.s, ars.reader)
    loop.call_soon(ars.poll)
    loop.call_soon(ars.water, 0)
    # loop.call_soon(ars.turnOn, 0)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        ars.allOff()
        loop.close()


if __name__=="__main__":
    main3()

