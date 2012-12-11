# Artcast
# Copyright (c) 2012, Timothy M. Shead
#
# Contact: shead.timothy@gmail.com
#
# Artcast is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Artcast is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Artcast.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import functools
import json
import logging
import logging.handlers
import os
import socket
import struct
import sys
import threading

import tornado.httpserver
import tornado.ioloop
import tornado.web

def template_path(*paths):
  templates = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")
  for path in paths:
    candidate = os.path.join(templates, path)
    if os.path.exists(candidate):
      return candidate

class handler(tornado.web.RequestHandler):
  """Add some useful functionality common to all handlers."""
  def accept(self, *server_types):
    # First, sort the client's accepted MIME types in order of preference ...
    client_types = [("*/*", "q=1.0")]
    if "accept" in self.request.headers:
      client_types = [mime_type.split(";") for mime_type in self.request.headers["accept"].split(",")]
    client_types = [(type[0], float(type[1].split("=")[1]) if len(type) > 1 else 1.0) for type in client_types]
    client_types = sorted(client_types, key=lambda x: x[1], reverse=True)

    # Iterate over the server's accepted MIME types in order of preference ...
    for client_type, quality in client_types:
      for server_type in server_types:
        if client_type == server_type:
          return server_type
        if client_type == "*/*":
          return server_type
        if client_type[-2:] == "/*" and client_type.split("/")[0] == server_type.split("/")[0]:
          return server_type
    raise tornado.web.HTTPError(406, "Accepted MIME types are: %s" % server_types)

sources = {}
class artcasts_handler(handler):
  """Handles each request for the list of available artcasts."""
  def get(self):
    self.accepted = self.accept("application/json", "text/html")
    self.set_header("Content-Type", self.accepted)
    if self.accepted == "text/html":
      self.render(template_path("artcasts.html"))
    elif self.accepted == "application/json":
      results = []
      for key, source in sources.items():
        results.append(source)
        results[-1]["key"] = key
      results = sorted(results, key=lambda x: x["key"])
      self.write(json.dumps(results))

class artcast_handler(handler):
  """Handles each request for an artcast."""
  callbacks = set()
  @staticmethod
  def message(key, data):
    """Called whenever a new artcast value has been received."""
    for callback in artcast_handler.callbacks.copy():
      callback(key, data)

  @tornado.web.asynchronous
  def get(self, key):
    """Called when a client requests an artcast."""
    self.accepted = self.accept("text/plain", "application/json", "text/html")
    if self.accepted == "text/html":
      self.render(template_path("%s.html" % key, "artcast.html"), key=key)
      return

    self.key = key
    artcast_handler.callbacks.add(self.get_result)

  def get_result(self, key, data):
    """Called when a new artcast value has been received."""
    if self.key != key:
      return
    artcast_handler.callbacks.remove(self.get_result)
    if self.accepted == "application/json":
      self.write(json.dumps(data))
    elif self.accepted == "text/plain":
      self.write(str(data))
    self.set_header("Content-Type", self.accepted)
    self.set_header("Access-Control-Allow-Origin", artcast_handler.access_control_allow_origin)

    if key in sources and "license" in sources[key] and sources[key]["license"] is not None:
      self.set_header("Link", '<%s>; rel="license"; title="%s"' % (sources[key]["license"]["uri"], sources[key]["license"]["title"]))

    self.finish()

def register_source(group, port):
  """Listens for source registration messages."""
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
  except:
    pass
  sock.bind(("", port))
  mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
  while True:
    key, data = json.loads(sock.recv(4096))
    if key not in sources:
      sources[key] = {}
    sources[key].update(data)

def receive_data(group, port):
  """Listens for new artcast values."""
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
  except:
    pass
  sock.bind(("", port))
  mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
  while True:
    key, data = json.loads(sock.recv(4096))
    if key not in sources:
      sources[key] = {}
    tornado.ioloop.IOLoop.instance().add_callback(functools.partial(artcast_handler.message, key, data))

def combined_log_format(handler):
  logging.getLogger().info(
    "{remote_ip} - {user} {timestamp} \"{method} {path} {version}\" {status} - \"{referer}\" \"{user_agent}\"".format(
      remote_ip = handler.request.remote_ip,
      user = handler.current_user if handler.current_user is not None else "-",
      timestamp = datetime.datetime.utcnow().strftime("[%d/%b/%Y:%H:%M:%S +0000]"),
      method = handler.request.method,
      path = handler.request.path,
      version = handler.request.version,
      status = handler.get_status(),
      referer = handler.request.headers["Referer"] if "Referer" in handler.request.headers else "-",
      user_agent = handler.request.headers["User-Agent"] if "User-Agent" in handler.request.headers else "-"
      ))

def handle_callback_exception(callback):
  logging.getLogger("artcast.error").error("Exception in callback %r", callback, exc_info=True)

if __name__ == "__main__":
  import optparse
  parser = optparse.OptionParser()
  parser.add_option("--access-control-allow-origin", default="*", help="Cross origin resource sharing control.  Default: %default")
  parser.add_option("--access-log", default=None, help="Access log file.  Default: %default")
  parser.add_option("--access-log-count", type="int", default=100, help="Maximum number of access log files.  Default: %default")
  parser.add_option("--access-log-size", type="int", default=10000000, help="Maximum access log file size in bytes.  Default: %default")
  parser.add_option("--client-port", type="int", default=8888, help="Client request input port.  Default: %default")
  parser.add_option("--daemonize", default=False, action="store_true", help="Daemonize the server.")
  parser.add_option("--data-group", default="224.1.1.1", help="Multicast group for receiving data messages.  Default: %default")
  parser.add_option("--data-port", type="int", default=5007, help="Multicast port for receiving data messages.  Default: %default")
  parser.add_option("--error-log", default=None, help="Error log file.  Default: %default")
  parser.add_option("--error-log-count", type="int", default=100, help="Maximum number of error log files.  Default: %default")
  parser.add_option("--error-log-size", type="int", default=10000000, help="Maximum error log file size in bytes.  Default: %default")
  parser.add_option("--pidfile", default=None, help="PID file.  Default: %default")
  parser.add_option("--register-group", default="224.1.1.1", help="Multicast group for receiving registration messages.  Default: %default")
  parser.add_option("--register-port", type="int", default=5008, help="Multicast port for receiving registration messages.  Default: %default")
  parser.add_option("--uid", type="int", default=None, help="Drop privileges to uid.  Default: %default")
  parser.add_option("--verbose", default=False, action="store_true",  help="Enable debugging output.")
  options, arguments = parser.parse_args()

  if options.verbose:
    for key in sorted(options.__dict__.keys()):
      sys.stderr.write("%s : %s\n" % (key, options.__dict__[key]))

  artcast_handler.access_control_allow_origin = options.access_control_allow_origin

  if options.daemonize:
    import daemon
    context = daemon.DaemonContext()
    context.open()

  # Setup logging ...
  access_log = logging.getLogger()
  access_log.propagate = False
  access_log.setLevel(logging.INFO)
  access_log.handlers = []
  access_log.addHandler(logging.StreamHandler())

  if options.access_log is not None:
    access_log.handlers = []
    access_log.addHandler(logging.handlers.RotatingFileHandler(options.access_log, "a", options.access_log_size, options.access_log_count))

  error_log = logging.getLogger("artcast.error")
  error_log.propagate = False
  error_log.setLevel(logging.INFO)
  error_log.handlers = []
  error_log.addHandler(logging.StreamHandler())

  if options.error_log is not None:
    error_log.handlers = []
    error_log.addHandler(logging.handlers.RotatingFileHandler(options.error_log, "a", options.error_log_size, options.error_log_count))

  data_thread = threading.Thread(target=receive_data, kwargs={"group" : options.data_group, "port" : options.data_port})
  data_thread.daemon = True
  data_thread.start()

  registration_thread = threading.Thread(target=register_source, kwargs={"group" : options.register_group, "port" : options.register_port})
  registration_thread.daemon = True
  registration_thread.start()

  application = tornado.web.Application(
    [
      ("/", tornado.web.RedirectHandler, {"url" : "/artcasts", "permanent":False}),
      ("/artcasts", artcasts_handler),
      ("/artcasts/(.*)", artcast_handler)
    ],
    static_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "content"),
    static_url_prefix = "/content/",
    log_function = combined_log_format
    )

  server = tornado.httpserver.HTTPServer(application)
  server.bind(options.client_port)
  if options.uid is not None:
    os.setuid(options.uid)
  server.start(1)
  try:
    if options.pidfile:
      with open(options.pidfile, "wb") as pidfile:
        pidfile.write(str(os.getpid()))

    loop = tornado.ioloop.IOLoop.instance()
    loop.handle_callback_exception = handle_callback_exception
    loop.start()
  finally:
    if options.pidfile:
      os.unlink(options.pidfile)

