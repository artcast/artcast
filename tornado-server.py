import datetime
import threading
import time

import tornado.ioloop
import tornado.web

listeners = []
def event_source():
  def wrap_callback(callback, data):
    def implementation():
      callback(data)
    return implementation
  while True:
    if len(listeners):
      data = datetime.datetime.now()
      for listener in listeners:
        tornado.ioloop.IOLoop.instance().add_callback(wrap_callback(listener, data))
    time.sleep(5)

thread = threading.Thread(target=event_source)
thread.daemon = True
thread.start()

class MainHandler(tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def get(self):
    listeners.append(self.result)

  def result(self, data):
    listeners.remove(self.result)
    self.write(str(data))
    self.finish()

application = tornado.web.Application([
  (r"/", MainHandler)
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

