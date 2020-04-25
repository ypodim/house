#!/usr/bin/env python3

import asyncio
import json
import requests
import datetime as dt
import time

from sensors.daytime import Daytime
from sensors.adc import ADC
from actuators.relays import Relay
from actuators.rf433 import RFManager
from jobs.garage import Garage, Doorbell, Lights, LutronActions
from lutron import Lutron
from logger import Logger

class Sensors(object):
    adc=ADC()
    daytime=Daytime()
    def __init__(self):
        pass

class homeAI(object):
    VMurl = "http://localhost/data/"
    def __init__(self, loop):
        self.loop = loop
        self.lutron = Lutron(self.loop)
        self.sensors = Sensors()
        self.actuators = {}
        self.actuators["relay"] = Relay()
        self.actuators["rf"] = RFManager()
        self.actuators["lutron"] = self.lutron
        self.jobs = {}
        self.state = {}
        self.actions = {}
        self.jobs["garage"] = Garage()
        self.jobs["doorbell"] = Doorbell()
        self.jobs["lights"] = Lights()
        self.jobs["lutron"] = LutronActions()
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
        sensors = dict(adc=self.sensors.adc, daytime=self.sensors.daytime)
        data = dict(sensors=sensors, state=self.state)
        r = None
        try:
            r = requests.put(homeAI.VMurl, data=dict(datastr=json.dumps(data, default=str)))
        except:
            print("oops, network problems with {}".format(homeAI.VMurl))

        if r:
            for i, action in enumerate(json.loads(r.content).get("actions")):
                self.actions[time.time()] = action

        self.loop.call_later(0.1, self.pushDataToVM)

if __name__=="__main__":

    time.sleep(5) # wait for network to come up while booting
    loop = asyncio.get_event_loop()
    
    hai = homeAI(loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    loop.close() 


    
    