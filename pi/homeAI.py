import tornado.ioloop
import logging
import json
import requests
import datetime as dt
import time
from tornado.options import define, options

from sensors.daytime import Daytime
from sensors.adc import ADC
from actuators.relays import Relay
from actuators.rf433 import RFManager
from jobs.garage import Garage, Doorbell, Lights, Daytime as DaytimeJob

define("VMurl", default="http://localhost/data/", help="VM remote url to post data", type=str)

class Sensors(object):
    adc=ADC()
    daytime=Daytime()
    def __init__(self):
        pass

class homeAI(object):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.sensors = Sensors()
        self.actuators = {}
        self.actuators["relay"] = Relay()
        self.actuators["rf"] = RFManager()
        self.jobs = {}
        self.state = {}
        self.actions = {}
        self.jobs["garage"] = Garage()
        self.jobs["doorbell"] = Doorbell()
        self.jobs["lights"] = Lights()
        self.jobs["daytime"] = DaytimeJob()
        tornado.ioloop.IOLoop.instance().call_later(0, self.pushDataToVM)
        tornado.ioloop.IOLoop.instance().call_later(0, self.runJobs)

    def runJobs(self):
        for jname, job in self.jobs.items():
            job.run(self.sensors, self.actuators, self.state, self.actions)
        tornado.ioloop.IOLoop.instance().call_later(0.05, self.runJobs)

    def pushDataToVM(self):
        sensors = dict(adc=self.sensors.adc, daytime=self.sensors.daytime)
        data = dict(sensors=sensors, state=self.state)
        r = None
        try:
            r = requests.put(options.VMurl, data=dict(datastr=json.dumps(data, default=str)))
        except:
            print("oops, network problems with {}".format(options.VMurl))

        if r:
            for i, action in enumerate(json.loads(r.content).get("actions")):
                self.actions[time.time()] = action

        tornado.ioloop.IOLoop.instance().call_later(0.1, self.pushDataToVM)

if __name__=="__main__":
    hai = homeAI()
    print("running")
    tornado.ioloop.IOLoop.current().start()

    
    