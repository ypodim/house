import datetime as dt
import urllib.request
import json
import time
import ssl
from logger import Logger

import platform
if platform.system() != "Linux":
    ssl._create_default_https_context = ssl._create_unverified_context

class Daytime():
    def __init__(self):
        self.dawn_time = None
        self.dusk_time = None
        self.last_update = 0
        self.isDaytime = None
        self.timeLeft = None
        self.log = Logger(__class__.__name__)

    def get_dtime_obj(self, dtstr):
        str_format = "%Y-%m-%dT%H:%M:%S%z"
        res = dt.datetime.strptime(dtstr, str_format)
        res = res.replace(tzinfo=dt.timezone.utc).astimezone(tz=None)
        return res

    def requestTimes(self):
        lat = "37.487846"
        lon = "-122.236115"
        try:
            url = "https://api.sunrise-sunset.org/json?lat={}&lng={}&formatted=0".format(lat, lon)
            req = urllib.request.Request(url)   
            content = urllib.request.urlopen(req).read()
            data = json.loads(content.decode("ascii"))
        except:
            if platform.system() != "Linux":
                self.log.log("sun: network down?")
            return

        self.dawn_time = self.get_dtime_obj(data["results"]["sunrise"]).replace(tzinfo=None).time()
        self.dusk_time = self.get_dtime_obj(data["results"]["sunset"]).replace(tzinfo=None).time()
        self.last_update = time.time()
        
    def calcMetadata(self):
        if self.dawn_time==None or self.dusk_time==None:
            return

        self.isDaytime = True
        now = dt.datetime.now()
        if (now.time() < self.dawn_time or now.time() > self.dusk_time):
            self.isDaytime = False

        if self.isDaytime:
            self.timeLeft = dt.datetime.combine(dt.date.today(), self.dusk_time) - now
        else:
            self.timeLeft = dt.datetime.combine(dt.date.today(), self.dawn_time) - now

    def __get__(self, instance, owner):
        if time.time() - self.last_update > 3600:
            self.requestTimes()
        self.calcMetadata()
        return dict(dawn_time=self.dawn_time, dusk_time=self.dusk_time, isDaytime=self.isDaytime, timeLeft=self.timeLeft)

if __name__=="__main__":
    dtime = Daytime()
    dtime.requestTimes()
    print(dtime.__get__(None, None))
