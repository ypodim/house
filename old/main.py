import os
import tornado.ioloop
import tornado.web
import redis
import json
import datetime

# https://www.a2hosting.com/web-hosting
# https://www.hostwinds.com/vps/linux


def entry2string(temperature, tstamp):
    return "%s" % json.dumps(dict(temperature=temperature, tstamp=tstamp))
def string2entry(valstr):
    dic = json.loads(valstr)
    return dic["temperature"], dic["tstamp"]

def pushMeasurement(db, temperature, tstamp):
    key = tstamp
    val = entry2string(temperature, tstamp)
    db.set(key, val)

def getMeasurements(db):
    result = []
    for k in db.keys():
        valstr = db.get(k)
        temperature, tstamp = string2entry(valstr)
        result.append((tstamp, temperature))
    return result

class TestHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db
    def get(self):
        for k in self.db.keys():
            self.db.delete(k)

class GraphHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db
    def get(self):
        self.render("index.html")

def fakeData():
    return json.loads(open("sample.data").read()).get("measurements")

class DefaultHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db
    def get(self, path=""):
        self.write("ok")

class DataHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db
    def get(self, path=""):
        measurements = getMeasurements(self.db)
        if not measurements:
            measurements = fakeData()
        # measurements = list(filter(lambda x: x[1].isdigit(), measurements))
        measurements = list(map(lambda x: [datetime.datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S.%f').timestamp(), getNumber(x[1])], measurements))
        measurements = sorted(measurements, key=lambda x: x[0])
        measurements = measurements[-200:]
        self.write(dict(measurements=measurements))
    def post(self, path=""):
        data = json.loads(self.request.body)
        temperature = data.get("temperature")
        tstamp = data.get("tstamp")
        pushMeasurement(self.db, temperature, tstamp)
        self.write(dict(status="ok"))

def getNumber(string):
    while not string[0].isdigit():
        string = string[1:]
    return float(string)

def main():
    db = redis.from_url(os.environ.get("REDIS_URL"))
    settings = dict(template_path="html", static_path="static", debug=True)
    app = tornado.web.Application([
        (r"/graph", GraphHandler, dict(db=db)),
        (r"/test", TestHandler, dict(db=db)),
        (r"/data/?(.*)", DataHandler, dict(db=db)),
        (r"/(.*)", DefaultHandler, dict(db=db)),
        
        (r'/favicon.ico', tornado.web.StaticFileHandler),
        (r'/static/', tornado.web.StaticFileHandler),
    ], **settings)

    port = int(os.environ.get("PORT", 5000))
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()

