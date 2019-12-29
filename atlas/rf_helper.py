import json
try:
    from rpi_rf import RFDevice
except:
    print("*** Error: must run on raspberry")

class RFManager:
    def __init__(self):
        self.codes = None
    def getCode(self, outletFamily, btn, value):
        if self.codes == None:
            with open("codes.json") as f:
                self.codes = json.loads(f.read())
        return self.codes[outletFamily][btn][value]
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