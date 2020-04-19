import datetime as dt

class Job:
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
                actuators["relay"].toggle()
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
    def run(self, sensors, actuators, state, actions):
        # Process actions
        for a in list(actions.keys()).copy():
            if actions[a] == "garage.light.toggle":
                if "isGarageLightOn" not in state:
                    state["isGarageLightOn"] = False
                state["isGarageLightOn"] = not state["isGarageLightOn"]

                newstate = "on" if state["isGarageLightOn"] else "off"
                actuators["rf"].txCode("0306", "2", newstate)
                del actions[a]

class Daytime(Job):
    def dayTimeLeft(self, dawn_time, dusk_time):
        tomorrow = dt.date.today() + dt.timedelta(days=1)
        next_event = dt.datetime.now()
        if dawn_time != None and dusk_time != None:
            if 1:#isDaytime:
                next_event = dt.datetime.combine(tomorrow, dusk_time.time())
            else: 
                next_event = dt.datetime.combine(tomorrow, dawn_time.time())
        
        timeleft = next_event - dt.datetime.now().replace(microsecond=0)
        while timeleft > dt.timedelta(days=1):
            timeleft -= dt.timedelta(days=1)
        return "%s" % timeleft

    def run(self, sensors, actuators, state, actions):
        # Process sensors
        daytimeLeft = self.dayTimeLeft(sensors.daytime.get("dawn_time"), sensors.daytime.get("dusk_time"))
        if (1 < 450):
            state["isDaytime"] = True
        else:
            state["isDaytime"] = False


# logic: is the bell btn pressed
# action: if bell btn is pressed send message
# logic: is it day or night
# action: if daylight changes, toggle light
