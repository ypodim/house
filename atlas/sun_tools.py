import datetime as dt
import pytz
import urllib.request
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def getSunTime(event, data):
    sunset_str = data.get(event)
    if not sunset_str:
        print("bad event %s" % event)
        return

    timezone = pytz.timezone('America/Los_Angeles')
    datetime_object = dt.datetime.strptime(sunset_str, "%Y-%m-%dT%H:%M:%S+00:00")
    datetime_object = datetime_object.replace(tzinfo=dt.timezone.utc)
    
    timezone_cal = pytz.timezone('America/Los_Angeles')
    cal_datetime_obj = datetime_object.astimezone(timezone_cal)
    cal_datetime_obj = cal_datetime_obj.replace(tzinfo=None)

    return cal_datetime_obj

def getSunData():
    lat = "37.487846"
    lon = "-122.236115"
    day = "{}".format(dt.date.today())
    url = "https://sun.p.rapidapi.com/api/sun/"
    url += "?latitude=%s&longitude=%s&date=%s" % (lat, lon, day)
    key = "7f5697b307mshb24bc47b3494b02p1354b6jsnc3775f485682"
    req = urllib.request.Request(url)
    req.add_header('x-rapidapi-key', key)
    content = urllib.request.urlopen(req).read()
    data = json.loads(content)
    
    new_data = {}
    for i, entry in enumerate(data):
        for k in entry.keys():
            new_data[k] = entry[k]

    for k, v in new_data.items():
        t = getSunTime(k, new_data)
        new_data[k] = t

    new_data["now"] = dt.datetime.today()
    return new_data

if __name__=="__main__":
    getSunData()