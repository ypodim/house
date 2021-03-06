import json
import sys
import time
import os
from collections import defaultdict
from logger import Logger
try:
    from rpi_rf import RFDevice
except:
    print("must run on raspberry")
    RFDevice = {}

class Plug:
    def __init__(self, outletFamily, btn, codes):
        self.of = outletFamily
        self.btn = btn
        self.codes = codes
        self.log = Logger(__class__.__name__)
    def json(self):
        return dict(of=self.of, btn=self.btn, status=self.status)
    def tx(self, plugstate, pin=2):
        if plugstate not in self.codes:
            self.log.log("state %s not found: of:%s btn:%s" % (plugstate, self.of, self.btn))
            return None
        code = self.codes[plugstate]
        if RFDevice:
            rfdevice = RFDevice(pin)
            rfdevice.enable_tx()
            rfdevice.tx_repeat = 10
            try:
                rfdevice.tx_code(code, 1, 187, 24)
                rfdevice.cleanup()
            except:
                self.log.log("unexpected error: %s" % sys.exc_info()[0])
                return None
        return code

class RFManager:
    def __init__(self, data_path):
        self.plugs = []
        with open("%s/codes.json" % data_path) as f:
            for plug in json.loads(f.read()).get("plugs"):
                self.plugs.append(Plug(plug["outletFamily"], plug["btn"], plug["codes"]))
        self.log = Logger(__class__.__name__)
        self.log.log("RFManager loaded %s plugs" % len(self.plugs))
    def getPlug(self, outletFamily, btn):
        res = list(filter(lambda x: x.of==outletFamily and x.btn==btn, self.plugs))
        if not res:
            self.log.log("plug not found: of:%s btn:%s val:%s" % (outletFamily, btn, val))
            return None
        return res[0]
    def txCode(self, outletFamily, btn, val):
        plug = self.getPlug(outletFamily, btn)
        if not plug:
            return None
        return plug.tx(val)

class RFReceiver(object):
    def __init__(self, pin=3):
        self.rfdevice = RFDevice(pin)
        self.rfdevice.enable_rx()
    def recv(self):
        try:
            timestamp = None
            while True:
                rxtstamp = self.rfdevice.rx_code_timestamp
                if rxtstamp and rxtstamp != timestamp:
                    timestamp = self.rfdevice.rx_code_timestamp
                    print("{} [pulselength {}]", (str(self.rfdevice.rx_code), str(self.rfdevice.rx_pulselength)))
                time.sleep(0.01)
        except KeyboardInterrupt:
            self.rfdevice.cleanup()


if __name__=="__main__":
    # rf = RFManager()
    # print(rf.txCode("0306", "2", sys.argv[1]))
    rfrecv = RFReceiver()
    rfrecv.recv()



'''
#include <RCSwitch.h>

RCSwitch mySwitch = RCSwitch();

void setup() {
  mySwitch.enableTransmit(10);
  mySwitch.setPulseLength(180);
  mySwitch.setRepeatTransmit(5);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
//  mySwitch.send(4283651, 24); // 0306-4 on
//  mySwitch.send(4281795, 24); // 0306-2 on
  delay(500);
  
  digitalWrite(LED_BUILTIN, LOW);
//  mySwitch.send(4283660, 24); // 0306-4 off
  mySwitch.send(4281804, 24); // 0306-2 off
  delay(500);
}
'''