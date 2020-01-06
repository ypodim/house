import urllib.request
import json

class Ngrok(object):
    def __init__(self):
        pass
    def getLocalInfo(self):
        req = urllib.request.Request(url="http://127.0.0.1:4040/api/tunnels")
        try:
            with urllib.request.urlopen(req) as f:
                data = json.loads(f.read().decode('utf-8'))
                return data.get("tunnels")[0].get("public_url")
        except urllib.error.URLError:
            print("ConnectionRefusedError")
            return None
            
    def setup(self):
        pass


if __name__=="__main__":
    ng = Ngrok()
    print(ng.getLocalInfo())

