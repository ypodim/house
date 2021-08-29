import datetime as dt
import tornado.ioloop
import time
from logger import Logger

class Job:
    def __init__(self):
        self.log = Logger(__class__.__name__)
    def run(self, sensors, state, actions):
        print("%s not implemented" % self.__class__.__name__)

class Garage(Job):
    def run(self, sensors, actuators, state, actions):
        # Process sensors
        garage_sensor = 0
        if (sensors.arduinoserial.value["adc"]):
            garage_sensor = int(sensors.arduinoserial.value["adc"][2])
        # gmax = "garage_max"
        # gmin = "garage_min"
        # if gmax not in state: state[gmax] = 0
        # if gmin not in state: state[gmin] = 1000
        # if garage_sensor > state[gmax]: state[gmax] = garage_sensor
        # if garage_sensor < state[gmin]: state[gmin] = garage_sensor
        # print("garage: {}\t- {}".format(state[gmin], state[gmax]))
        if (garage_sensor < 250):
            state["isGarageDoorOpen"] = True
        else:
            state["isGarageDoorOpen"] = False

        # Process actions
        for a in list(actions.keys()).copy():
            if actions[a] == "garage.door.toggle":
                garageRelay = 7
                actuators.arduserial.set(garageRelay, False)
                time.sleep(0.1)
                actuators.arduserial.set(garageRelay, True)
                time.sleep(0.2)
                actuators.arduserial.set(garageRelay, False)
                del actions[a]
            elif actions[a].startswith("relay."):
                pin = actions[a][-1]
                pin = int(pin)
                current_value = actuators.arduserial.get()[pin]
                actuators.arduserial.set(pin, (current_value == 0))
                del actions[a]

class Valve():
    def __init__(self, pin, duration, startAt, ars):
        now = dt.datetime.now()
        self.pin = pin
        self.name = "zone%s" % (pin+1)
        self.lastOn = now
        self.lastOff = now
        self.duration = duration
        self.startAt = startAt
        self.ars = ars
        self.armed = False
        self._ison = False
        self.log = Logger(__class__.__name__)
    def isOn(self):
        return self._ison
        # return self.ars.get()[self.pin]
    def turnOn(self):
        self.ars.turnOn(self.pin)
        self.lastOn = dt.datetime.now()
        self.armed = False
        self._ison = True
    def turnOff(self):
        self.ars.turnOff(self.pin)
        self.lastOff = dt.datetime.now()
        self.armed = False
        self._ison = False
    def run(self, clearToTurnOn):
        now = dt.datetime.now()
        if self.isOn():
            runtime = now - self.lastOn
            targetDuration = dt.timedelta(minutes=self.duration)
            if (runtime >= targetDuration):
                self.turnOff()
                self.log.action("%s is on, turning off" % self.name)
                return 0
        else:
            if (now.hour == self.startAt.hour and now.minute == self.startAt.minute):
                self.armed = True
            if (self.armed and clearToTurnOn):
                self.turnOn()
                self.log.action("%s turning on!" % self.name)
                return 1
        return -1
    
class Irrigation(Job):
    def init(self, actuators, state):
        # self.times = [5, 7, 14, 4, 11, 5]
        # self.times = [3,3,7,3,7,2]
        # self.times = [4,6,6,1,10,6]
        startAt = dt.time(hour=19, minute=15)

        state["irrigation"] = {}
        irs = state["irrigation"]
        irs["times"] = [4,6,6,1,10,6]

        self.valves = []
        for i in range(len(irs["times"])):
            self.valves.append(Valve(i, irs["times"][i], startAt, actuators.arduserial))

    def run(self, sensors, actuators, state, actions):
        if "irrigation" not in state:
            self.init(actuators, state)
        # irs = state["irrigation"]

        clearToTurnOn = True
        for i in range(len(state["irrigation"]["times"])):
            if self.valves[i].isOn():
                clearToTurnOn = False

        for i in range(len(state["irrigation"]["times"])):
            valve = self.valves[i]
            turnedOn = valve.run(clearToTurnOn)
            if turnedOn == 1:
                clearToTurnOn = False

        for a in list(actions.keys()).copy():
            if actions[a].startswith("irrigation"):
                # actuators.relays.water.toggle()
                actuators.arduserial.water(0)
                del actions[a]

class StreatNumberSign(Job):
    def run(self, sensors, actuators, state, actions):
        if "streatnumbersign" not in state:
            state["streatnumbersign"] = 1
            self.isOn = False
            self.actuators = actuators

        signRelay = 6
        now = dt.datetime.now().time()
        threshold = dt.time(hour=23, minute=0)
        duskTime = sensors.daytime.value["dusk_time"]
        if threshold > duskTime: # threshold < 12am
            shouldBeOn = (now > duskTime and now < threshold)
        else: 
            shouldBeOn = (now > duskTime or now < threshold)

        if (shouldBeOn == self.isOn): return

        self.log.log("street sign: turning %s" % shouldBeOn)
        self.actuators.arduserial.set(signRelay, shouldBeOn)
        self.isOn = shouldBeOn

class LutronActions(Job):
    def run(self, sensors, actuators, state, actions):
        if "lutron" not in state:
            state["lutron"] = {}

        if sensors.daytime.value["isDaytime"]:
            deviceId = "7"
            value = actuators.lutron.get(deviceId)
            if value != None and value > 0:
                actuators.lutron.set(deviceId, 0)
                self.log.log("it's daytime, turning off %s" % deviceId)

        # Process actions
        for a in list(actions.keys()).copy():
            if actions[a].startswith("lutron."):
                deviceId = actions[a].split('.')[1]
                # if actions[a] not in state["lutron"]:
                #     state["lutron"][actions[a]]
                actuators.lutron.toggle(deviceId)
                del actions[a]
        
class Doorbell(Job):
    def run(self, sensors, actuators, state, actions):
        # Process sensors
        doorbell_sensor = sensors.adc[1]
        if (doorbell_sensor < 450):
            state["isDoorbellPressed"] = True
        else:
            state["isDoorbellPressed"] = False


class Lights(Job):
    def toggleGarageLight(self, times=4):
        self.state["isGarageLightOn"] = not self.state["isGarageLightOn"]
        newstate = "on" if self.state["isGarageLightOn"] else "off"
        self.actuators.rf.txCode("0306", "2", newstate)
        print("garage light going %s" % newstate)
        if times > 0:
            tornado.ioloop.IOLoop.instance().call_later(0.2, self.toggleGarageLight, times=times-1)

    def toggleRFSwitch(self, rfswitch: str) -> None:
        _, rffamily, rfid = rfswitch.split('.')
        self.state[rfswitch] = not self.state[rfswitch]
        newstate = "on" if self.state[rfswitch] else "off"
        self.actuators.rf.txCode(rffamily, rfid, newstate)
        print(rffamily, rfid, newstate)

    def run(self, sensors, actuators, state, actions):
        self.state = state
        self.actuators = actuators
        # Process actions
        for a in list(actions.keys()).copy():
            if actions[a].startswith("rf.0306."):
                if actions[a] not in state:
                    state[actions[a]] = False

                self.toggleRFSwitch(actions[a])
                del actions[a]

            elif actions[a] == "garage.light.toggle":
                if "isGarageLightOn" not in state:
                    state["isGarageLightOn"] = False

                self.toggleGarageLight(times=0)
                del actions[a]

