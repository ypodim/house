#!/usr/bin/env python3

import asyncio
import re
import time
import datetime as dt
from logger import Logger

class Configuration(object):
    _conf = [
    {"ID" : 13,"Name" : "Pico", "Area" : {"Name" : "Hallway"}},
    {"ID" : 4, "Name" : "Island Pendants", "Area" : {"Name" : "Kitchen"}},
    {"ID" : 5, "Name" : "Sconces","Area" : {"Name" : "Master Bedroom"}},
    {"ID" : 6, "Name" : "Shower Lights","Area" : {"Name" : "Master Bathroom"}},
    {"ID" : 7, "Name" : "Sink Lights","Area" : {"Name" : "Master Bathroom"}},
    {"ID" : 8, "Name" : "Exhaust Fan","Area" : {"Name" : "Master Bathroom"}},
    {"ID" : 9, "Name" : "Main Lights","Area" : {"Name" : "Guest Bathroom"}},
    {"ID" : 10,"Name" : "Exhaust Fan","Area" : {"Name" : "Guest Bathroom"}},
    {"ID" : 2, "Name" : "Main Lights","Area" : {"Name" : "Kitchen"}},
    {"ID" : 3, "Name" : "Main Lights","Area" : {"Name" : "Living Room"}},
    {"ID" : 11,"Name" : "Sink Pendants","Area" : {"Name" : "Kitchen"}},
    {"ID" : 12,"Name" : "Main Lights","Area" : {"Name" : "Hallway"}},
    {"ID" : 14,"Name" : "Main Lights","Area" : {"Name" : "Master Bedroom"}}
    ]
    @staticmethod
    def get(deviceid):
        res = filter(lambda x: x["ID"]==int(deviceid), Configuration._conf)
        return(list(res))
    def getIDs():
        res = map(lambda x: x["ID"], Configuration._conf)
        return(list(res))
 
class Lutron(asyncio.Protocol):
    def __init__(self, loop):
        self.loop = loop
        self.log = Logger(__class__.__name__)
        self._state = {}
        self.initialized = False

    def connection_made(self, transport):
        self.log.log("connection established")
        self.transport = transport
 
    def data_received(self, data):
        if data.decode() == "login: ":
            self.log.log("sending login")
            self.transport.write(b"lutron\r\n")
        elif data.decode() == "password: ":
            self.log.log("sending password")
            self.transport.write(b"integration\r\n")
        else:
            if not self.initialized:
                self.initialized = True
                for deviceid in Configuration.getIDs():
                    # print(deviceid)
                    self.query(deviceid)
                    time.sleep(0.1)

            # self.processData(data.decode())
            asyncio.ensure_future(self.processData(data.decode()))
    
    def toggle(self, deviceid):
        value = 0
        deviceid = 4
        data = "#OUTPUT,%s,1,%s\r\n" % (deviceid, value)
        self.transport.write(data.encode())

    def query(self, deviceid):
        data = "?OUTPUT,%s,1\r\n" % (deviceid)
        self.transport.write(data.encode())

    async def processData(self, data):
        value = 0
        msgre = re.compile("\~(\S+?),(\S+)\r\n$")
        self._wait_v = ""

        mobj = msgre.search(data)
        if not mobj:
            # self.log.log("unknown pattern found: %s" % data)
            return

        if(mobj.group(1) == self._wait_v or mobj.group(1) == "ERROR"):
            self._return_data = []
            self._return_data.append(mobj.group(1))
            self._return_data.append(mobj.group(2).split(","))
            self._wait_v = ""
        
        cmdtype = mobj.group(1)
        cmd = mobj.group(2)
        deviceid, b, value = cmd.split(",")
        device = Configuration.get(deviceid)

        line = "device:{} value:{}".format(deviceid, value)
        self.log.data(line)
        self._state[deviceid] = value

    def connection_lost(self, exc):
        self.log.log('The server closed the connection')
        self.log.log('Stop the event loop')
        self.loop.stop()

    def __str__(self):
        return "lutron"
    def __getattr__(self, attr):
        if attr == "value":
            # await self.processData
            return "asdf: %s" % attr
        else:
            return "unknown attr: %s" % attr

if __name__=="__main__":
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(lambda: Lutron(loop), '192.168.1.58', 23)
    loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    loop.close() 
