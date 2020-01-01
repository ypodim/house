import urllib.request
import json
import time
import ssl


ssl._create_default_https_context = ssl._create_unverified_context

def getStatus(plugstr="of:0362 btn:3"):
    with urllib.request.urlopen('http://atlas:8888/rf433/') as f:
        raw = f.read()
        data = json.loads(raw)
        for plug in data.get("status"):
            if plug.startswith(plugstr):
                status = plug.split(" ")[-1]
                print(" {} ".format(status), end="\r", flush=True)

while 1:
    getStatus()
    time.sleep(0.05)
