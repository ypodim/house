import tornado.ioloop
import tornado.web
import tornado.options
import tornado.log
import json
import datetime
import logging
import time

from homeAI import homeAI

class TemperatureHandler(tornado.web.RequestHandler):
    def post(self):
        logging.info("%s: %s" % (datetime.datetime.now(), self.get_argument("temperature")))
        self.write(dict(status="ok"))
    def get(self):
        self.render("index.html")

class SensorHandler(tornado.web.RequestHandler):
    def initialize(self, brain):
        self.brain = brain
    # /sensors/light
    def put(self):
        params = self.request.path.split('/')[2:]
        val = self.get_argument("value")
        logging.info("Value:%s" % val)
        if len(params) == 2:
            outletFamily = params[0]
            btn = params[1]
            result = self.brain.rf.txCode(outletFamily, btn, val)
            self.write(dict(status="ok", result=result))
            return
        self.write(dict(status="error: expected 2 params, got %s" % len(params), value=val))
    def get(self):
        self.write(dict(status=self.brain.sensors.getStatus()))

class RF433Handler(tornado.web.RequestHandler):
    def initialize(self, brain):
        self.brain = brain
    # /rf433/0306/1
    def put(self):
        params = self.request.path.split('/')[2:]
        val = self.get_argument("value")
        logging.info("Value:%s" % val)
        if len(params) == 2:
            outletFamily = params[0]
            btn = params[1]
            result = self.brain.rf.txCode(outletFamily, btn, val)
            self.write(dict(status="ok", result=result))
            return
        self.write(dict(status="error: expected 2 params, got %s" % len(params), value=val))
    def get(self):
        plugs = []
        for plug in self.brain.rf.getStatus():
            plug["action"] = "on"
            if plug["status"] == "on":
                plug["action"] = "off"
            plugs.append(plug)
        self.render("index.html", daytime=self.brain.daytime, plugs=plugs)
        
class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("ok")


def main():
    tornado.options.parse_command_line()
    # tornado.log.enable_pretty_logging()
    access_log = logging.getLogger('tornado.access')
    access_log.info("starting up")

    brain = homeAI()

    settings = dict(template_path="html", static_path="static", debug=True)
    app = tornado.web.Application([
        (r"/temperature.*", TemperatureHandler),
        (r"/sensor/.*", SensorHandler, dict(brain=brain)),
        (r"/rf433.*", RF433Handler, dict(brain=brain)),
        (r"/", DefaultHandler),
        
        (r'/favicon.ico', tornado.web.StaticFileHandler),
        (r'/static/', tornado.web.StaticFileHandler),
    ], **settings)

    try:
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.add_callback(brain.root)
        pc = tornado.ioloop.PeriodicCallback(brain.periodic, 1000)
        pc.start()
        app.listen(8888)
        io_loop.start()
    except KeyboardInterrupt:
        logging.info('stopping services...') 

if __name__ == "__main__":
    main()


