import json
import logging
from collections import defaultdict
try:
    from rpi_rf import RFDevice
except:
    logging.error("must run on raspberry")
    RFDevice = {}

class Plug:
    def __init__(self, outletFamily, btn, codes):
        self.of = outletFamily
        self.btn = btn
        self.codes = codes
        self.status = None
    def __repr__(self):
        return "of:%s btn:%s status:%s" % (self.of, self.btn, self.status)
    def getStatus(self):
        return self.status
    def tx(self, plugstate, pin=17):
        if plugstate not in self.codes:
            logging.error("state %s not found: of:%s btn:%s" % (plugstate, self.of, self.btn))
            return None
        code = self.codes[plugstate]
        if RFDevice:
            rfdevice = RFDevice(pin)
            rfdevice.enable_tx()
            rfdevice.tx_repeat = 10
            rfdevice.tx_code(code, 1, 187, 24)
            rfdevice.cleanup()
        self.status = plugstate
        return code

class RFManager:
    def __init__(self):
        self.plugs = []
        with open("codes.json") as f:
            for plug in json.loads(f.read()).get("plugs"):
                self.plugs.append(Plug(plug["outletFamily"], plug["btn"], plug["codes"]))
        logging.info("RFManager loaded %s plugs" % len(self.plugs))
    def getPlug(self, outletFamily, btn):
        res = list(filter(lambda x: x.of==outletFamily and x.btn==btn, self.plugs))
        if not res:
            logging.error("plug not found: of:%s btn:%s val:%s" % (outletFamily, btn, val))
            return None
        return res[0]
    def getPlugStatus(self, outletFamily, btn):
        plug = self.getPlug(outletFamily, btn)
        if not plug:
            return None
        return plug.getStatus()
    def txCode(self, outletFamily, btn, val):
        plug = self.getPlug(outletFamily, btn)
        if not plug:
            return None
        return plug.tx(val)
    def getStatus(self):
        return ["%s"%p for p in self.plugs]
        

if __name__=="__main__":
    import sys
    rf = RFManager()
    print(rf.txCode("0362", "3", sys.argv[1]))
