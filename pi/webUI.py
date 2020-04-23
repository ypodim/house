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
from collections.abc import MutableMapping
from tornado.options import define, options

define("port", default=80, help="run on the given port", type=int)

class Store(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.store = dict(data=None)
        self.last_update = 0
        self.actions = []
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.last_update = datetime.datetime.now()
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        return "%s" % self.store

    def addAction(self, action):
        self.actions.append(action)
    def getActions(self, clear=True):
        actions = self.actions
        if clear: self.actions = []
        return actions
    def save(self, data):
        self["data"] = data
    def get(self):
        return dict(data=self.store["data"], last_update="%s" % self.last_update)

    def __keytransform__(self, key):
        return key

class DataHandler(tornado.web.RequestHandler):
    def initialize(self, store):
        self.store = store
    def put(self):
        # params = self.request.path.split('/')[2:]
        data = json.loads(self.get_argument("datastr"))
        self.store.save(data)
        self.write(dict(actions=self.store.getActions()))
    def get(self):
        self.write(self.store.get())

class ActionHandler(tornado.web.RequestHandler):
    def initialize(self, store):
        self.store = store
    def put(self):
        action = self.get_argument("action")
        self.store.addAction(action)
        self.write(dict(result="ok", actions=self.store.getActions(clear=False)))
    def get(self):
        self.write(dict(actions=self.store.getActions(clear=False)))

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("raw.html")

class Application(tornado.web.Application):
    def __init__(self, store):
        handlers = [
            (r"/data/.*", DataHandler, dict(store=store)),
            (r"/actions", ActionHandler, dict(store=store)),
            (r"/", DefaultHandler),
            (r'/favicon.ico', tornado.web.StaticFileHandler),
            (r'/static/', tornado.web.StaticFileHandler),
        ]
        settings = dict(
            blog_title=u"Tornado Blog",
            template_path=os.path.join(os.path.dirname(__file__), "html"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/auth/login",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

async def main(shutdown_event):
    # tornado.options.parse_command_line()
    # tornado.log.enable_pretty_logging()
    access_log = logging.getLogger('tornado.access')
    access_log.info("starting up")

    store = Store()
    app = Application(store)
    
    io_loop = tornado.ioloop.IOLoop.current()
    # pc = tornado.ioloop.PeriodicCallback(brain.periodic, 1000)
    # pc.start()
    app.listen(options.port)
    await shutdown_event.wait()

if __name__ == "__main__":
    shutdown_event = tornado.locks.Event()
    try:
        tornado.ioloop.IOLoop.current().run_sync(lambda: main(shutdown_event))
    except KeyboardInterrupt:
        print("time to die")
        shutdown_event.set()



