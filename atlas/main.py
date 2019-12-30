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
            code = self.brain.rf.getCode(outletFamily, btn, val)
            self.brain.rf.tx(code)
            self.write(dict(status="ok", value=val))
            return
        self.write(dict(status="error: expected 2 params, got %s" % len(params), value=val))
    def get(self):
        self.write(dict(status=self.brain.rf.getStatus()))

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("ok")


def main():
    # tornado.options.parse_command_line()
    tornado.log.enable_pretty_logging()
    access_log = logging.getLogger('tornado.access')
    access_log.info("starting up")

    brain = homeAI()
    brain.start()

    settings = dict(template_path="html", static_path="static", debug=True)
    app = tornado.web.Application([
        (r"/temperature.*", TemperatureHandler),
        (r"/rf433.*", RF433Handler, dict(brain=brain)), 
        (r"/", DefaultHandler),
        
        (r'/favicon.ico', tornado.web.StaticFileHandler),
        (r'/static/', tornado.web.StaticFileHandler),
    ], **settings)

    try:
        app.listen(8888)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logging.info('stopping services...')
        brain.running = 0
        brain.join()    

if __name__ == "__main__":
    main()


