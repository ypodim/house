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

define("port", default=8888, help="run on the given port", type=int)

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class PushDataHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    def open(self):
        PushDataHandler.waiters.add(self)

    def on_message(self, message):
        # self.write_message(u"You said: {} {}".format(message, time.time()))
        pass

    def on_close(self):
        PushDataHandler.waiters.remove(self)

    @classmethod
    def push(cls, message):
        for waiter in cls.waiters:
            waiter.write_message(message)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/websocket", PushDataHandler),
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
    access_log = logging.getLogger('tornado.access')
    access_log.info("starting up")

    app = Application()
    
    io_loop = tornado.ioloop.IOLoop.current()
    app.listen(options.port)
    await shutdown_event.wait()

if __name__ == "__main__":
    shutdown_event = tornado.locks.Event()
    try:
        tornado.ioloop.IOLoop.current().run_sync(lambda: main(shutdown_event))
    except:
        print("time to die")
        shutdown_event.set()



