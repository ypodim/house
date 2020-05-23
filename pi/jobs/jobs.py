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
        garage_sensor = sensors.adc[0]
        # gmax = "garage_max"
        # gmin = "garage_min"
        # if gmax not in state: state[gmax] = 0
        # if gmin not in state: state[gmin] = 1000
        # if garage_sensor > state[gmax]: state[gmax] = garage_sensor
        # if garage_sensor < state[gmin]: state[gmin] = garage_sensor
        # print("garage: {}\t- {}".format(state[gmin], state[gmax]))
        if (garage_sensor < 400):
            state["isGarageDoorOpen"] = True
        else:
            state["isGarageDoorOpen"] = False

        # Process actions
        for a in list(actions.keys()).copy():
            if actions[a] == "garage.door.toggle":
                garagePin = 0
                actuators.relays.garage.set(1)
                time.sleep(0.1)
                actuators.relays.garage.set(0)
                del actions[a]

class Irrigation(Job):
    def run(self, sensors, actuators, state, actions):
        if "irrigation" not in state:
            state["irrigation"] = {}
            state["irrigation"]["last_start"] = dt.datetime.now()
            state["irrigation"]["last_end"] = dt.datetime.now()

        irrState = state["irrigation"]

        waterFor = dt.timedelta(minutes=10)

        if actuators.relays.water.isOn():
            if dt.datetime.now() > irrState["last_start"] + waterFor:
                actuators.relays.water.set(0)
                irrState["last_end"] = dt.datetime.now()
                self.log.log("turning OFF front-lawn water")
        else:
            now = dt.datetime.now()
            if now.hour == 21 and now.minute == 00:
                actuators.relays.water.set(1)
                irrState["last_start"] = now
                self.log.log("turning ON front-lawn water")

        for a in list(actions.keys()).copy():
            if actions[a].startswith("irrigation"):
                actuators.relays.water.toggle()
                del actions[a]

        

class LutronActions(Job):
    def run(self, sensors, actuators, state, actions):
        # Process actions
        for a in list(actions.keys()).copy():
            if actions[a] == "kitchen.pendants":
                actuators.lutron.toggle(actions[a])
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

