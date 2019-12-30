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
        codeon = self.rf.getCode(outletFamily, btn, "on")
        codeoff = self.rf.getCode(outletFamily, btn, "off")
        
        status = "off"
        try:
            status = self.rf.status[outletFamily][btn]
        except:
            pass

        if status == "on":
            self.rf.tx(codeoff)
        else:
            self.rf.tx(codeon)

    def run(self):
        while self.running:
            self.looplights()
            
            time.sleep(3)
        self.log.info("thread exiting")