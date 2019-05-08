import os
# import tornado.httpserver
import tornado.ioloop
import tornado.web
import time
import json
# import redis
# import random
# import datetime
# from operator import attrgetter, itemgetter

# https://www.a2hosting.com/web-hosting
# https://www.hostwinds.com/vps/linux

class DefaultHandler(tornado.web.RequestHandler):
    def get(self, path=""):
        self.write(dict(asdf="Ok"))

def main():
    settings = dict(template_path="html", static_path="static", debug=True)
    app = tornado.web.Application([
        (r"/(.*)", DefaultHandler),
        (r'/favicon.ico', tornado.web.StaticFileHandler),
        (r'/static/', tornado.web.StaticFileHandler),
    ], **settings)

    port = int(os.environ.get("PORT", 5000))
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()

