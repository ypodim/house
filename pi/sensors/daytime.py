import datetime as dt
import urllib.request
import json
import time
import ssl

import platform
if platform.system() != "Linux":
    ssl._create_default_https_context = ssl._create_unverified_context

class Daytime():
    def __init__(self):
        self.dawn_time = None
        self.dusk_time = None
        self.last_update = 0
        self.isDaytime = None

    def dayTimeLeft(self):
        tomorrow = dt.date.today() + dt.timedelta(days=1)
        next_event = dt.datetime.now()
        if self.dawn_time != None and self.dusk_time != None:
            if self.isDaytime:
                next_event = dt.datetime.combine(tomorrow, self.dusk_time.time())
            else: 
                next_event = dt.datetime.combine(tomorrow, self.dawn_time.time())
        
        timeleft = next_event - dt.datetime.now().replace(microsecond=0)
        while timeleft > dt.timedelta(days=1):
            timeleft -= dt.timedelta(days=1)
        return "%s" % timeleft

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

            self.dawn_time = self.get_dtime_obj(data["results"]["sunrise"])
            self.dusk_time = self.get_dtime_obj(data["results"]["sunset"])
            self.last_update = time.time()
        except:
            if platform.system() != "Linux":
                print("sun: network down?")

    def __get__(self, instance, owner):
        if time.time() - self.last_update > 3600:
            self.requestTimes()
        sunrise = "%s" % self.dawn_time
        sunset = "%s" % self.dusk_time
        return dict(sunrise=sunrise, sunset=sunset, timeleft=self.dayTimeLeft())

if __name__=="__main__":
    for k,v in getSunData().items():
        print(k,v)