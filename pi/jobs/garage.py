


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
                print("open door!")
                del actions[a]
        
class Doorbell(Job):
    def run(self, sensors, actuators, state, actions):
        # Process sensors
        doorbell_sensor = sensors.adc[1]
        # dmax = "doorbell_max"
        # dmin = "doorbell_min"
        # if dmax not in state: state[dmax] = 0
        # if dmin not in state: state[dmin] = 1000
        # if doorbell_sensor > state[dmax]: state[dmax] = doorbell_sensor
        # if doorbell_sensor < state[dmin]: state[dmin] = doorbell_sensor
        # print("doorbell: {}\t- {}".format(state[dmin], state[dmax]))
        if (doorbell_sensor < 450):
            state["isDoorbellPressed"] = True
        else:
            state["isDoorbellPressed"] = False


# action: open garage door 
# logic: is the garage door open or closed
# logic: is the bell btn pressed
# action: if bell btn is pressed send message
# logic: is it day or night
# action: if daylight changes, toggle light
# action: toggle rf433 switches
