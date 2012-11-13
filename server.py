import functools
import json
import os
import socket
import threading

import tornado.ioloop
import tornado.web

class handler(tornado.web.RequestHandler):
  """Add some useful functionality common to all handlers."""
  def accept(self, *mime_types):
    for mime_type in mime_types:
      for element in self.request.headers["accept"].split(","):
        if mime_type == element.split(";")[0]:
          return mime_type

class number_handler(handler):
  """Handles each request for a number."""
  callbacks = set()
  @staticmethod
  def message(key, data):
    """Called whenever a new number has been received."""
    for callback in number_handler.callbacks.copy():
      callback(key, data)

  @tornado.web.asynchronous
  def get(self, key):
    """Called when a client requests a number."""
    if self.accept("application/json", "text/html") == "text/html":
      self.render("number.html", key=key)
      return

    self.key = key
    number_handler.callbacks.add(self.get_result)

  def get_result(self, key, data):
    """Called when a new number has been received."""
    if self.key != key:
      return
    number_handler.callbacks.remove(self.get_result)
    self.write(str(data))
    self.finish()

application = tornado.web.Application(
  [
  (r"/numbers/(.*)", number_handler)
  ],
  debug = True,
  static_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "content"),
  static_url_prefix = "/content/"
  )

print os.path.join(os.path.abspath(os.path.dirname(__file__)), "content")

def udp_source():
  """Listens for new numbers."""
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.bind(("", 51423))
  while True:
    key, data = json.loads(s.recv(4096))
    tornado.ioloop.IOLoop.instance().add_callback(functools.partial(number_handler.message, key, data))

if __name__ == "__main__":
  udp_thread = threading.Thread(target=udp_source)
  udp_thread.daemon = True
  udp_thread.start()

  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()

