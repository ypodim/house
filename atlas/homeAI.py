import threading
import time
import logging
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
        self.log.info("light status is %s" % status)

        if status == "on":
            self.log.info("turning lights off")
            self.rf.txCode(outletFamily, btn, "off")
            time.sleep(3)
        else:
            self.log.info("turning lights on")
            self.rf.txCode(outletFamily, btn, "on")
            time.sleep(1)

    def run(self):
        while self.running:
            self.looplights()
        self.log.info("thread exiting")