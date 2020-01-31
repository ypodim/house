import tornado.ioloop
import tornado.options
import tornado.locks
import tornado.websocket
import json
import logging
import os

tornado.options.define("port", default=9999, help="port", type=int)

class DataStructure(object):
    def __init__(self):
        self.data = None
    def update(self, data):
        self.data = data
    def get(self):
        return json.dumps(self.data)

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("ok")

class DataHandler(tornado.web.RequestHandler):
    def initialize(self, ds):
        self.ds = ds
    def get(self):
        self.write(self.ds.get())
    def post(self):
        data = self.get_argument("data")
        data = json.loads(data)
        self.ds.update(data)
        self.write("ok {}".format(data))

class PushDataHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    def open(self):
        PushDataHandler.waiters.add(self)
    def on_message(self, message):
        pass
    def on_close(self):
        PushDataHandler.waiters.remove(self)
    @classmethod
    def push(cls, message):
        for waiter in cls.waiters:
            waiter.write_message(message)

class Application(tornado.web.Application):
    def __init__(self, ds):
        handlers = [
            (r"/websocket", PushDataHandler),
            (r"/", DefaultHandler),
            (r"/data", DataHandler, dict(ds=ds)),
        ]
        settings = dict(
            # xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/auth/login",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

async def main(shutdown_event):
    ds = DataStructure()
    tornado.options.parse_command_line()
    access_log = logging.getLogger('tornado.access')
    access_log.info("starting up")
    app = Application(ds)
    io_loop = tornado.ioloop.IOLoop.current()
    app.listen(tornado.options.options.port)
    await shutdown_event.wait()

if __name__ == "__main__":
    shutdown_event = tornado.locks.Event()
    try:
        tornado.ioloop.IOLoop.current().run_sync(lambda: main(shutdown_event))
    except KeyboardInterrupt:
        print("time to die")
        shutdown_event.set()
