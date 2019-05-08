import os
import tornado.ioloop
import tornado.web
import redis

# https://www.a2hosting.com/web-hosting
# https://www.hostwinds.com/vps/linux

class DefaultHandler(tornado.web.RequestHandler):
    def initialize(self, db):
        self.db = db
    def get(self, path=""):
        temp = self.db.get("temperature")
        if temp:
            temp = temp.decode("utf-8")
            self.write(dict(temperature=temp))
        else:
            self.write(dict(error="key temperature does not exist"))
    def post(self, path=""):
        temp = self.get_argument("temperature")
        print(temp)
        self.db.set("temperature", temp)
        self.write(dict(status="ok"))

def main():
    db = redis.from_url(os.environ.get("REDIS_URL"))
    settings = dict(template_path="html", static_path="static", debug=True)
    app = tornado.web.Application([
        (r"/(.*)", DefaultHandler, dict(db=db)),
        (r'/favicon.ico', tornado.web.StaticFileHandler),
        (r'/static/', tornado.web.StaticFileHandler),
    ], **settings)

    port = int(os.environ.get("PORT", 5000))
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()


