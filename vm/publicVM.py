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
        self.cmds = {}
    def dataUpdate(self, data):
        self.data = data
    def cmdUpdate(self, cmd):
        for k,v in cmd.items():
            self.cmds[k] = v
    def getData(self):
        return self.data
    def getCmds(self):
        return self.cmds
    def resetCmds(self):
        self.cmds = {}

class DefaultHandler(tornado.web.RequestHandler):
    def initialize(self, ds):
        self.ds = ds
    def get(self):
        self.write("ok")
    def post(self):
        cmd = self.get_argument("cmd")
        cmd = json.loads(cmd)
        self.ds.cmdUpdate(cmd)
        self.write(cmd)
    def options(self):
        self.set_status(204)
        self.finish()
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

class DataHandler(tornado.web.RequestHandler):
    def initialize(self, ds):
        self.ds = ds
    def get(self):
        self.write(json.dumps(self.ds.getData()))
    def post(self):
        data = self.get_argument("data")
        data = json.loads(data)
        self.ds.dataUpdate(data)

        response = dict(cmds=self.ds.getCmds())
        self.ds.resetCmds()
        self.write(json.dumps(response))
        
class PushDataHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    def check_origin(self, origin):
        return True
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
            (r"/", DefaultHandler, dict(ds=ds)),
            (r"/data", DataHandler, dict(ds=ds)),
        ]
        settings = dict(
            # xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/auth/login",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

def clb(dataStructure):
    msg = dataStructure.getData()
    PushDataHandler.push(json.dumps(msg))
    tornado.ioloop.IOLoop.instance().call_later(1, clb, dataStructure)

async def main(shutdown_event):
    ds = DataStructure()
    tornado.options.parse_command_line()
    access_log = logging.getLogger('tornado.access')
    access_log.info("starting up")
    app = Application(ds)
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.call_later(0, clb, ds)
    app.listen(tornado.options.options.port)
    await shutdown_event.wait()

if __name__ == "__main__":
    shutdown_event = tornado.locks.Event()
    try:
        tornado.ioloop.IOLoop.current().run_sync(lambda: main(shutdown_event))
    except KeyboardInterrupt:
        print("time to die")
        shutdown_event.set()
