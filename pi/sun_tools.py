import datetime as dt
import urllib.request
import json
import ssl

import platform
if platform.system() != "Linux":
    ssl._create_default_https_context = ssl._create_unverified_context

def get_dtime_obj(dtstr):
    str_format = "%Y-%m-%dT%H:%M:%S%z"
    res = dt.datetime.strptime(dtstr, str_format)
    res = res.replace(tzinfo=dt.timezone.utc).astimezone(tz=None)
    return res

def getSunData():
    result = {}
    lat = "37.487846"
    lon = "-122.236115"

    try:
        url = "https://api.sunrise-sunset.org/json?lat={}&lng={}&formatted=0".format(lat, lon)
        req = urllib.request.Request(url)   
        content = urllib.request.urlopen(req).read()
        data = json.loads(content.decode("ascii"))

        sunrise = get_dtime_obj(data["results"]["sunrise"])
        sunset = get_dtime_obj(data["results"]["sunset"])
        result = dict(sunrise=sunrise, sunset=sunset)
    except:
        if platform.system() != "Linux":
            print("sun: network down?")

    return result

if __name__=="__main__":
    for k,v in getSunData().items():
        print(k,v)