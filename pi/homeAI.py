import tornado.ioloop
import logging
import json
import requests
import datetime as dt
import time
from tornado.options import define, options

from rf_helper import RFManager
from garageDoor import GarageDoor
from sensors.daytime import Daytime
from sensors.adc import ADC

define("VMurl", default="http://localhost/data/", help="VM remote url to post data", type=str)

class Sensors(object):
    adc=ADC()
    daytime=Daytime()
    def __init__(self):
        pass

class homeAI(object):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.rf = RFManager()
        self.garageDoor = GarageDoor()
        self.sensors = Sensors()
        tornado.ioloop.IOLoop.instance().call_later(0, self.pushData)

    def pushData(self):
        data = dict(adc=self.sensors.adc, daytime=self.sensors.daytime)
        # print(self.sensors.daytime.last_update)
        r = None
        try:
            r = requests.put(options.VMurl, data=dict(sensors=json.dumps(data)))
        except:
            print("oops, network problems with {}".format(options.VMurl))

        if r:
            for i, action in enumerate(json.loads(r.content).get("actions")):
                print(i, action)

        tornado.ioloop.IOLoop.instance().call_later(1, self.pushData)

if __name__=="__main__":
    hai = homeAI()
    tornado.ioloop.IOLoop.current().start()

    
    