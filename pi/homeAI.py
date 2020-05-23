#!/usr/bin/env python3

import asyncio
import json
import requests
import datetime as dt
import time

from sensors.daytime import Daytime
from sensors.adc import ADC
from actuators.relays import Relays
from actuators.rf433 import RFManager
from jobs.jobs import Garage, Doorbell, Lights, LutronActions, Irrigation
from lutron import Lutron
from logger import Logger

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
        self.loop = loop
        self.lutron = Lutron(self.loop)
        self.sensors = Sensors()
        self.sensors.addSensor(ADC())
        self.sensors.addSensor(Daytime())
        self.sensors.addSensor(self.lutron)
        self.actuators = Actuators()
        self.actuators.relays = Relays()
        self.actuators.rf = RFManager()
        self.actuators.lutron = self.lutron
        self.jobs = {}
        self.state = {}
        self.actions = {}
        self.jobs["garage"] = Garage()
        self.jobs["doorbell"] = Doorbell()
        self.jobs["lights"] = Lights()
        self.jobs["lutron"] = LutronActions()
        self.jobs["irrigation"] = Irrigation()
        self.log = Logger(__class__.__name__)

        loop.call_later(0, self.pushDataToVM)
        loop.call_later(0, self.runJobs)
        coro = loop.create_connection(lambda: self.lutron, '192.168.1.58', 23)
        loop.run_until_complete(coro)

    def runJobs(self):
        for jname, job in self.jobs.items():
            job.run(self.sensors, self.actuators, self.state, self.actions)
        self.loop.call_later(0.05, self.runJobs)

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

        self.loop.call_later(0.1, self.pushDataToVM)

if __name__=="__main__":

    time.sleep(5) # wait for network to come up while booting
    loop = asyncio.get_event_loop()
    
    hai = homeAI(loop)
    # print(hai.sensors.values)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    loop.close()


    
    