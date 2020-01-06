import urllib.request
import json

class Ngrok(object):
    def __init__(self):
        pass
    def getLocalInfo(self):
        req = urllib.request.Request(url="http://127.0.0.1:4040/api/tunnels")
        with urllib.request.urlopen(req) as f:
            data = json.loads(f.read().decode('utf-8'))
            print(data)
    def setup(self):
        pass


if __name__=="__main__":
    ng = Ngrok()
    ng.getLocalInfo()

