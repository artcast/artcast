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

import json
import optparse
import os
import socket
import sys
import threading
import time

options = None
arguments = None
def parse():
  global options, arguments
  parser = optparse.OptionParser()
  parser.add_option("--daemonize", default=False, action="store_true", help="Daemonize the process.")
  parser.add_option("--data-port", type="int", default=5007, help="Multicast port for sending registration messages.  Default: %default")
  parser.add_option("--group", default="224.1.1.1", help="Multicast group for sending source messages.  Default: %default")
  parser.add_option("--pidfile", default=None, help="PID file.  Default: %default")
  parser.add_option("--registration-port", type="int", default=5008, help="Multicast port for sending data messages.  Default: %default")
  parser.add_option("--ttl", type="int", default=1, help="Multicast TTL.  Default: %default")
  parser.add_option("--uid", type="int", default=None, help="Drop privileges to uid.  Default: %default")
  parser.add_option("--verbose", default=False, action="store_true",  help="Enable debugging output.")
  options, arguments = parser.parse_args()

  if options.verbose:
    for key in sorted(options.__dict__.keys()):
      sys.stderr.write("%s : %s\n" % (key, options.__dict__[key]))

registration_socket = None
def register(key, description, provenance):
  global registration_socket
  if registration_socket is None:
    registration_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    registration_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, options.ttl)
  if options.verbose:
    sys.stderr.write("register %s : %s %s\n" % (key, description, provenance))
  registration_socket.sendto(json.dumps((key, {"description" : description, "provenance" : provenance})), (options.group, options.registration_port))

value_socket = None
def send(key, value):
  global value_socket
  if value_socket is None:
    value_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    value_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, options.ttl)
  if options.verbose:
    sys.stderr.write("send %s : %s\n" % (key, value))
  value_socket.sendto(json.dumps((key, value)), (options.group, options.data_port))
global_send = send

def register_source(key, description, provenance):
  while True:
    register(key, description, provenance)
    time.sleep(30.0)

class context:
  def __init__(self, key):
    self.key = key

  def send(self, value):
    global_send(self.key, value)

register_threads = []
data_threads = []
def add(target, key, description, provenance):
  register_threads.append(threading.Thread(target=register_source, kwargs={"key" : key, "description" : description, "provenance" : provenance}))
  register_threads[-1].daemon = True

  data_threads.append(threading.Thread(target=target, args=[context(key=key)]))
  data_threads[-1].daemon = True

def run():
  parse()

  if options.daemonize:
    import daemon
    context = daemon.DaemonContext()
    context.open()

  if options.uid is not None:
    os.setuid(options.uid)

  for thread in register_threads:
    thread.start()

  for thread in data_threads:
    thread.start()

  if options.pidfile:
    with open(options.pidfile, "wb") as pidfile:
      pidfile.write(str(os.getpid()))

  try:
    for thread in data_threads:
      thread.join()
  except KeyboardInterrupt:
    pass

  if options.pidfile:
    os.unlink(options.pidfile)
