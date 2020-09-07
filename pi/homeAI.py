#!/usr/bin/env python3

import asyncio
import os
import json
import requests
import datetime as dt
import time

from sensors.daytime import Daytime
from sensors.adc import ADC
from actuators.relays import Relays
from actuators.rf433 import RFManager
from jobs.jobs import Garage, Doorbell, Lights, LutronActions, Irrigation, StreatNumberSign
from lutron import Lutron
from logger import Logger
from arduinoSerial import ArduinoSerial

class Sensors(object):
    def __init__(self):
        self._sensors = {}
    def __getattr__(self, attr):
        if attr == "values":
            result = {}
            for sname, s in self._sensors.items():
                result[sname] = s.value
            return result
        else:
            return self._sensors[attr]
    def addSensor(self, sensor):
        sname = str(sensor)
        self._sensors[sname] = sensor
        self.__setattr__(sname, sensor)

class Actuators(object):
    def __init__(self):
        pass

class Jobs(object):
    def __init__(self):
        pass

class homeAI(object):
    VMurl = "http://localhost/data/"
    def __init__(self, loop):
        data_path = "%s/data" % os.path.dirname(__file__)
        print(data_path)
        self.loop = loop
        ars = ArduinoSerial(loop, None)

        self.lutron = Lutron(self.loop)
        self.sensors = Sensors()
        self.sensors.addSensor(ADC())
        self.sensors.addSensor(Daytime())
        self.sensors.addSensor(self.lutron)
        self.sensors.addSensor(ars)
        self.actuators = Actuators()
        self.actuators.relays = Relays()
        self.actuators.rf = RFManager(data_path)
        self.actuators.lutron = self.lutron
        self.actuators.arduserial = ars
        self.jobs = {}
        self.state = {}
        self.actions = {}
        self.jobs["garage"] = Garage()
        self.jobs["doorbell"] = Doorbell()
        self.jobs["lights"] = Lights()
        self.jobs["lutron"] = LutronActions()
        self.jobs["irrigation"] = Irrigation()
        self.jobs["streatnumbersign"] = StreatNumberSign()
        self.log = Logger(__class__.__name__)

        loop.call_later(0, self.pushDataToVM)
        loop.call_later(0, self.runJobs)
        coro = loop.create_connection(lambda: self.lutron, '192.168.1.58', 23)
        loop.run_until_complete(coro)
        loop.add_reader(ars.s, ars.reader)
        loop.call_soon(ars.poll)

    def runJobs(self):
        for jname, job in self.jobs.items():
            job.run(self.sensors, self.actuators, self.state, self.actions)
        self.loop.call_later(0.5, self.runJobs)

    def pushDataToVM(self):
        data = dict(sensors=self.sensors.values, state=self.state)
        r = None
        try:
            r = requests.put(homeAI.VMurl, data=dict(datastr=json.dumps(data, default=str)))
        except:
            print("oops, network problems with {}".format(homeAI.VMurl))

        if r:
            for i, action in enumerate(json.loads(r.content).get("actions")):
                self.actions[time.time()] = action
                self.log.action(action)

        self.loop.call_later(0.5, self.pushDataToVM)

if __name__=="__main__":
    # import sys
    # if (len(sys.argv) > 1):
    time.sleep(10) # wait for network to come up while booting
        
    loop = asyncio.get_event_loop()
    hai = homeAI(loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        hai.actuators.arduserial.allOff()
    loop.close()


    
    