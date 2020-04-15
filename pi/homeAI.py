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
from jobs.garage import Garage, Doorbell

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
        self.jobs = {}
        self.state = {}
        self.actions = {}
        self.jobs["garage"] = Garage()
        self.jobs["doorbell"] = Doorbell()
        tornado.ioloop.IOLoop.instance().call_later(0, self.pushDataToVM)
        tornado.ioloop.IOLoop.instance().call_later(0, self.runJobs)

    def runJobs(self):
        for jname, job in self.jobs.items():
            job.run(self.sensors, self.actuators, self.state, self.actions)
        tornado.ioloop.IOLoop.instance().call_later(0.2, self.runJobs)

    def pushDataToVM(self):
        data = dict(adc=self.sensors.adc, daytime=self.sensors.daytime)
        r = None
        try:
            r = requests.put(options.VMurl, data=dict(sensors=json.dumps(data)))
        except:
            print("oops, network problems with {}".format(options.VMurl))

        if r:
            for i, action in enumerate(json.loads(r.content).get("actions")):
                self.actions[time.time()] = action

        tornado.ioloop.IOLoop.instance().call_later(1, self.pushDataToVM)

if __name__=="__main__":
    hai = homeAI()
    tornado.ioloop.IOLoop.current().start()

    
    