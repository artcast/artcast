import httplib
import time

while True:
  connection = httplib.HTTPConnection("localhost:8888")
  connection.request("GET", "/artcasts/test/now")
  print connection.getresponse().read()
