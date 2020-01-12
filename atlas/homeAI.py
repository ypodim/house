import tornado.ioloop
import time
import logging
import random
import datetime as dt
from rf_helper import RFManager
from sun_tools import getSunData
from ngrok import Ngrok

class homeAI(object):
    def __init__(self):
        self.rf = RFManager()
        self.log = logging.getLogger(self.__class__.__name__)
        self.lastsun = 0
        self.dawn_time = 0
        self.dusk_time = 0
        self.daytime = 0

    def root(self):
        tornado.ioloop.IOLoop.instance().call_later(0, self.loopsuntimes)
        tornado.ioloop.IOLoop.instance().call_later(5, self.looplights)

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
        self.daytime = self.dawn_time < now and now < self.dusk_time
        if self.daytime:
            new_status = "off"
            
        self.rf.txCode(outletFamily, btn, new_status)
        
        sleep_time = random.random() * sleep_multiplier
        while sleep_time < 0.5:
            sleep_time = random.random() * sleep_multiplier

        # self.log.info("%s: sleeping for %s" % (new_status, sleep_time))
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
        # now = sun_data.get("now")
        # print("dawn:\t{}".format(dawn_time))
        # print("now:\t{}".format(now))
        # print("dusk:\t{}".format(dusk_time))
        # self.log.info("sun: sleeping for {}".format(sleep_time))
        sleep_time = 3600 * 24
        tornado.ioloop.IOLoop.instance().call_later(sleep_time, self.loopsuntimes)


    def periodic(self):
        # print("this is periodic {}".format(time.time()))
        pass

if __name__=="__main__":
    hai = homeAI()
    hai.loopsuntimes()
    hai.looplights()
    print(hai.daytime)
    
    