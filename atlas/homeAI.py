import threading
import time
import logging
import random
from rf_helper import RFManager

class homeAI(threading.Thread):
    def __init__(self):
        super(homeAI, self).__init__()
        self.running = 1
        self.rf = RFManager()
        self.log = logging.getLogger(self.__class__.__name__)

    def looplights(self):
        outletFamily = "0362"
        btn = "3"
        status = self.rf.getPlugStatus(outletFamily, btn)

        new_status = "on"
        sleep_multiplier = 5
        if status == "on":
            sleep_multiplier = 5
            new_status = "off"

        self.rf.txCode(outletFamily, btn, new_status)
        
        sleep_time = random.random() * sleep_multiplier
        while sleep_time < 0.5:
            sleep_time = random.random() * sleep_multiplier

        # self.log.info("%s: sleeping for %s" % (new_status, sleep_time))
        time.sleep(sleep_time)

    def run(self):
        while self.running:
            self.looplights()
        self.log.info("thread exiting")