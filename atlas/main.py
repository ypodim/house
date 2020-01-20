import tornado.ioloop
import tornado.web
import tornado.options
import tornado.log
import tornado.locks
import tornado.websocket
import json
import datetime
import logging
import time
import os

from tornado.options import define, options

from homeAI import homeAI

define("port", default=8888, help="run on the given port", type=int)


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

class GarageDoorHandler(tornado.web.RequestHandler):
    def initialize(self, brain):
        self.brain = brain
    def put(self):
        val = self.get_argument("value")
        if val in ("1", "0"): self.brain.toggleGarageDoor()
        self.write(dict(status="ok", value=val))
    def get(self):
        self.write(dict(status=self.brain.garageDoor.isOpen, irval=self.brain.garageDoor.irval))

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
        self.render("index.html")

class PushDataHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    def open(self):
        PushDataHandler.waiters.add(self)

    def on_message(self, message):
        self.write_message(u"You said: {} {}".format(message, time.time()))

    def on_close(self):
        PushDataHandler.waiters.remove(self)

    @classmethod
    def push(cls, message):
        for waiter in cls.waiters:
            waiter.write_message(message)


class Application(tornado.web.Application):
    def __init__(self, brain):
        handlers = [
            (r"/websocket", PushDataHandler),
            (r"/temperature.*", TemperatureHandler),
            (r"/sensor/.*", SensorHandler, dict(brain=brain)),
            (r"/garagedoor.*", GarageDoorHandler, dict(brain=brain)),
            (r"/rf433.*", RF433Handler, dict(brain=brain)),
            (r"/", DefaultHandler),
            (r'/favicon.ico', tornado.web.StaticFileHandler),
            (r'/static/', tornado.web.StaticFileHandler),
        ]
        settings = dict(
            blog_title=u"Tornado Blog",
            template_path=os.path.join(os.path.dirname(__file__), "html"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            # ui_modules={"Entry": EntryModule},
            # xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/auth/login",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

async def main(shutdown_event):
    tornado.options.parse_command_line()
    # tornado.log.enable_pretty_logging()
    access_log = logging.getLogger('tornado.access')
    access_log.info("starting up")

    brain = homeAI()

    app = Application(brain)
    
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.add_callback(brain.root, PushDataHandler.push)
    pc = tornado.ioloop.PeriodicCallback(brain.periodic, 1000)
    pc.start()
    app.listen(options.port)
    await shutdown_event.wait()

if __name__ == "__main__":
    shutdown_event = tornado.locks.Event()
    try:
        tornado.ioloop.IOLoop.current().run_sync(lambda: main(shutdown_event))
    except:
        print("time to die")
        shutdown_event.set()



