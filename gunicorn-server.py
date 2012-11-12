import threading
import time
import datetime
import Queue

import selector # https://github.com/lukearno/selector/

listeners = []
def event_source():
  global listeners
  while True:
    if len(listeners):
      data = datetime.datetime.now()
      for listener in listeners:
        listener(data)
    time.sleep(5)

def wait():
  def make_sender(queue):
    def implementation(data):
      queue.put(data)
    return implementation
  queue = Queue.Queue()
  sender = make_sender(queue)
  listeners.append(sender)
  data = queue.get()
  listeners.remove(sender)
  return str(data)

thread = threading.Thread(target=event_source)
thread.daemon = True
thread.start()

@selector.pliant
def get_number(environ, start_response, id):
  data = id + ": " + wait()
  status = '200 OK'
  response_headers = [
    ('Content-type','text/plain'),
    ('Content-Length', str(len(data)))
    ]
  start_response(status, response_headers)
  return iter([data])

application = selector.Selector()
application.add("/numbers/{id}", GET = get_number)

