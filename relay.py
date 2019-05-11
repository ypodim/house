import serial
import time
import datetime
import ssl
import httplib2
import json
import os



port = "/dev/tty.usbserial-A601ECRN"
port = "/dev/ttyUSB0"
ssl._create_default_https_context = ssl._create_unverified_context

def play(error=True):
  duration = 0
  freq = 240
  if error:
    duration = 0.2
    freq = 440
    print("error")
  if duration:
    os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))

class Temperature:
  def __init__(self):
    self.lastSave = 0
  
  def post(self, string):
    now = "%s" % datetime.datetime.now()
    entry = dict(temperature=string, tstamp=now)
    url = "http://pool.asdf0.com/data"
    # url = "http://localhost:5000/data"
    headers = {'Content-Type': 'application/json'}
    h = httplib2.Http(".cache")
    (resp, content) = h.request(url, "POST", body=json.dumps(entry), headers=headers)
    print(resp, content)
    self.lastSave = time.time()

  def process(self, string):
    print(string)
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
          if string == "-1000.00":
            play()
          else:
            play(False)
          
          self.process(string)
          string = ""
        else:
          string += "%s" % c

        time.sleep(0.001)

if __name__=="__main__":
  t = Temperature()
  t.loop()
