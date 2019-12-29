import json
from collections import defaultdict
try:
    from rpi_rf import RFDevice
except:
    print("*** Error: must run on raspberry")

class RFManager:
    def __init__(self):
        self.codes = None
        self.status = defaultdict(dict)
    def getCode(self, outletFamily, btn, value):
        if self.codes == None:
            with open("codes.json") as f:
                self.codes = json.loads(f.read())
        result = self.codes[outletFamily][btn][value]
        # if outletFamily not in self.status:
        #     self.status[outletFamily] = {}
        self.status[outletFamily][btn] = value
        return result
    def getStatus(self):
        return self.status
    def tx(self, code, pin=17):
        rfdevice = RFDevice(pin)
        rfdevice.enable_tx()
        rfdevice.tx_repeat = 10
        rfdevice.tx_code(code, 1, 187, 24)
        rfdevice.cleanup()

if __name__=="__main__":
    import sys
    rf = RFManager()
    code = rf.getCode("0362", 3, sys.argv[1])
    rf.tx(code)