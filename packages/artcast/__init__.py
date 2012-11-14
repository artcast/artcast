import json
import optparse
import socket
import threading
import time

host = "localhost"
port = 51423
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
threads = []

def add(target):
  threads.append(threading.Thread(target=target))
  threads[-1].daemon = True

def send(key, value):
  s.sendto(json.dumps((key, value)), (host, port))

def run():
  parser = optparse.OptionParser()
  parser.add_option("--host", default="localhost", help="Server host.  Default: %default")
  parser.add_option("--port", type="int", default=51423, help="Server input port.  Default: %default")
  options, arguments = parser.parse_args()

  host = options.host
  port = options.port

  for thread in threads:
    thread.start()

  while True:
    try:
      time.sleep(1.0)
    except KeyboardInterrupt:
      break
