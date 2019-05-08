import serial
import time
import datetime
import ssl
import httplib2
import json

port = "/dev/tty.usbserial-A601ECRN"
port = "/dev/ttyUSB0"
ssl._create_default_https_context = ssl._create_unverified_context

class Temperature:
  def __init__(self):
    self.lastSave = 0
  
  def post(self, string):
    now = "%s" % datetime.datetime.now()
    entry = dict(temperature=string, tstamp=now)
    url = "http://pool.asdf0.com"
    # url = "http://localhost:5000"
    headers = {'Content-Type': 'application/json'}
    h = httplib2.Http(".cache")
    (resp, content) = h.request(url, "POST", body=json.dumps(entry), headers=headers)
    self.lastSave = time.time()

  def process(self, string):
    if time.time() - self.lastSave > 300:
      self.post(string)

  def loop(self):
    with serial.Serial(port, 9600, timeout=0.01) as ser:
      string = ""
      while 1:
        c = ser.read().decode("utf-8")
        if len(c) == 0 or ord(c) == 10:
          continue
        elif ord(c) == 13:
          if len(string) == 5:
            self.process(string)
          string = ""
        else:
          string += "%s" % c

        time.sleep(0.001)

if __name__=="__main__":
  t = Temperature()
  t.loop()
