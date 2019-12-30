import tornado.ioloop
import tornado.web
import tornado.options
import json
import datetime
import logging
from rf_helper import RFManager

class TemperatureHandler(tornado.web.RequestHandler):
    def post(self):
        print("%s: %s" % (datetime.datetime.now(), self.get_argument("temperature")))
        self.write(dict(status="ok"))
    def get(self):
        self.render("index.html")

class RF433Handler(tornado.web.RequestHandler):
    def initialize(self, rf):
        self.rf = rf
    # /rf433/0306/1
    def put(self):
        params = self.request.path.split('/')[2:]
        val = self.get_argument("value")
        if len(params) == 2:
            outletFamily = params[0]
            btn = params[1]
            code = self.rf.getCode(outletFamily, btn, val)
            self.rf.tx(code)
            self.write(dict(status="ok", value=val))
            return
        self.write(dict(status="error: expected 2 params, got %s" % len(params), value=val))
    def get(self):
        self.write(dict(status=self.rf.getStatus()))

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("ok")


def main():
    tornado.options.parse_command_line()
    logging.info("starting up")
    rf = RFManager()
    settings = dict(template_path="html", static_path="static", debug=True)
    app = tornado.web.Application([
        (r"/temperature.*", TemperatureHandler),
        (r"/rf433.*", RF433Handler, dict(rf=rf)), 
        (r"/", DefaultHandler),
        
        (r'/favicon.ico', tornado.web.StaticFileHandler),
        (r'/static/', tornado.web.StaticFileHandler),
    ], **settings)

    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()


