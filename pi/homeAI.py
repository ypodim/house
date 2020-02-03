import tornado.ioloop
import logging
import random
import json
import urllib.request
import urllib.parse
import datetime as dt
import time
from rf_helper import RFManager
from sun_tools import getSunData
from garageDoor import GarageDoor
from tornado.options import options

class homeAI(object):
    def __init__(self):
        self.rf = RFManager()
        self.garageDoor = None
        self.log = logging.getLogger(self.__class__.__name__)
        self.lastsun = 0
        self.dawn_time = None
        self.dusk_time = None
        self.daytime = 0
        self.lastDataPushTime = 0
        self.garageDoor = GarageDoor()

    def toggleGarageDoor(self):
        self.garageDoor.toggle()

    def root(self, websocketClb):
        self.websocketClb = websocketClb
        tornado.ioloop.IOLoop.instance().call_later(0, self.loopsuntimes)
        tornado.ioloop.IOLoop.instance().call_later(5, self.looplights)
        tornado.ioloop.IOLoop.instance().call_later(0, self.pushData)

    def pushData(self):
        self.garageDoor.pollState()
        garagemsg = dict(isopen=self.garageDoor.isOpen, irval=self.garageDoor.irval)

        tomorrow = dt.date.today() + dt.timedelta(days=1)
        next_event = dt.datetime.now()
        if self.dawn_time != None and self.dusk_time != None:
            if self.daytime:
                next_event = dt.datetime.combine(tomorrow, self.dusk_time)
            else: 
                next_event = dt.datetime.combine(tomorrow, self.dawn_time)
        
        timeleft = next_event - dt.datetime.now().replace(microsecond=0)
        while timeleft > dt.timedelta(days=1):
            timeleft -= dt.timedelta(days=1)

        sensors = dict(daylight=self.daytime, timeleft="{}".format(timeleft))
        msg = dict(garagedoor=garagemsg, plugs=self.rf.getStatus(), sensors=sensors)
        msgstr = json.dumps(msg)
        self.websocketClb(msgstr)

        if time.time() - self.lastDataPushTime > 1:
            data = urllib.parse.urlencode(dict(data=msgstr))
            data = data.encode('ascii')
            url = options.VMurl
            try:
                with urllib.request.urlopen(url, data) as f:
                    rawstr = f.read()
                    cmds = json.loads(rawstr)
                    print(cmds.get("cmds"))
            except:
                self.log.error("could not connect to {}".format(url))
            self.lastDataPushTime = time.time()
        
        tornado.ioloop.IOLoop.instance().call_later(0.1, self.pushData)

    def looplights(self):
        outletFamily = "0362"
        btn = "3"
        status = self.rf.getPlugStatus(outletFamily, btn)

        new_status = "on"
        sleep_multiplier = 5
        if status == "on":
            sleep_multiplier = 5
            new_status = "off"

        now = dt.datetime.today().time()
        if self.dawn_time != None and self.dusk_time != None:
            self.daytime = self.dawn_time < now and now < self.dusk_time
        if self.daytime:
            new_status = "off"
            
        self.rf.txCode(outletFamily, btn, new_status)
        
        sleep_time = random.random() * sleep_multiplier
        while sleep_time < 0.5:
            sleep_time = random.random() * sleep_multiplier

        tornado.ioloop.IOLoop.instance().call_later(sleep_time, self.looplights)

    def loopsuntimes(self):
        try:
            sun_data = getSunData()
        except:
            sleep_time = 10
            self.log.error("sun: network down? Trying again in {} seconds".format(sleep_time))
            tornado.ioloop.IOLoop.instance().call_later(sleep_time, self.loopsuntimes)
            return
        self.dawn_time = sun_data.get("dawn").time()
        self.dusk_time = sun_data.get("dusk").time()
        sleep_time = 3600 * 24
        tornado.ioloop.IOLoop.instance().call_later(sleep_time, self.loopsuntimes)

    def periodic(self):
        pass
        

if __name__=="__main__":
    hai = homeAI()
    hai.pushData()
    tornado.ioloop.IOLoop.current().start()

    
    