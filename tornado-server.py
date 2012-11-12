import functools
import socket
import threading

import tornado.ioloop
import tornado.web

class number_handler(tornado.web.RequestHandler):
  """Handles each request for a number."""
  callbacks = set()
  @staticmethod
  def message(data):
    """Called whenever a new number has been received."""
    for callback in number_handler.callbacks.copy():
      callback(data)

  @tornado.web.asynchronous
  def get(self):
    """Called when a client requests a number."""
    number_handler.callbacks.add(self.get_result)

  def get_result(self, data):
    """Called when a new number has been received."""
    number_handler.callbacks.remove(self.get_result)
    self.write(str(data))
    self.finish()

application = tornado.web.Application([
  (r"/", number_handler)
  ])

def udp_source():
  """Listens for new numbers."""
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.bind(("", 51423))
  while True:
    data = s.recv(4096)
    tornado.ioloop.IOLoop.instance().add_callback(functools.partial(number_handler.message, data))

if __name__ == "__main__":
  udp_thread = threading.Thread(target=udp_source)
  udp_thread.daemon = True
  udp_thread.start()

  application.listen(8888)
  tornado.ioloop.IOLoop.instance().start()

