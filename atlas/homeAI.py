import tornado.ioloop
import time
import logging
import random
from rf_helper import RFManager
from sun_tools import getSunData

class homeAI(object):
    def __init__(self):
        self.rf = RFManager()
        self.log = logging.getLogger(self.__class__.__name__)
        self.lastsun = 0
        self.daytime = True

    def root(self):
        tornado.ioloop.IOLoop.instance().call_later(0, self.looplights)
        tornado.ioloop.IOLoop.instance().call_later(0, self.loopsun)

    def looplights(self):
        outletFamily = "0362"
        btn = "3"
        status = self.rf.getPlugStatus(outletFamily, btn)

        new_status = "on"
        sleep_multiplier = 5
        if status == "on":
            sleep_multiplier = 5
            new_status = "off"

        if self.daytime:
            new_status = "off"
            
        self.rf.txCode(outletFamily, btn, new_status)
        
        sleep_time = random.random() * sleep_multiplier
        while sleep_time < 0.5:
            sleep_time = random.random() * sleep_multiplier

        # self.log.info("%s: sleeping for %s" % (new_status, sleep_time))
        tornado.ioloop.IOLoop.instance().call_later(sleep_time, self.looplights)

    def loopsun(self):
        sleep_time = 3600 * 24
        sun_data = getSunData()
        dawn_time = sun_data.get("dawn")
        dusk_time = sun_data.get("dusk")
        now = sun_data.get("now")
        # print("dawn:\t{}".format(dawn_time))
        # print("now:\t{}".format(now))
        # print("dusk:\t{}".format(dusk_time))
        self.daytime = dawn_time < now and now < dusk_time
        # self.log.info("sun: sleeping for {}".format(sleep_time))
        tornado.ioloop.IOLoop.instance().call_later(sleep_time, self.loopsun)


    def periodic(self):
        # print("this is periodic {}".format(time.time()))
        pass
