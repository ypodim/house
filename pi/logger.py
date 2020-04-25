import datetime as dt

class Logger:
    def __init__(self, name):
        self.name = name

    def data(self, msg):
        self.log(msg, "%s-data"%self.name)

    def log(self, msg, name=""):
        datefmt='%m-%d-%Y %H:%M:%S'
        filename = "data/example.log"
        tstamp = dt.datetime.now().strftime(datefmt)
        with open(filename, "a") as f:
            data = dict(tstamp=tstamp, name=name or self.name, msg=msg)
            f.write("%(tstamp)s:%(name)s:%(msg)s\n" % data)