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
    def name(id):
        device = Configuration.get(id)[0]
        return "%s in %s" % (device["Name"], device["Area"]["Name"])


class Processor:
    data = {}
    def load(self, fname="example.log"):
        with open(fname) as f:
            for line in f:
                _dtime = line[:19]
                raw = line[20:].strip().split(':', 1)
                _type = raw[0]
                ignore_types = ["Lutron", "RFManager", "Relay"]
                if _type == "Lutron-data":
                    device, value = raw[1].split()
                    device = device.split(':')[1]
                    devname = Configuration.name(device)
                    value = value.split(':')[1]
                    print(_dtime, devname, value)
                elif _type == "Job":
                    details = raw[1].split()
                    if details[0] == "turning" and details[-1] == "water":
                        onoff = details[1]
                        # print(_dtime, "lawn", onoff)
                elif _type == "homeAI-action":
                    if raw[1] == "garage.door.toggle":
                        pass
                elif _type in ignore_types:
                    pass
                else:
                    print(raw)


        



Processor().load()