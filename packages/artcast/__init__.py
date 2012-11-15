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

sock = None
options = None
threads = []

def add(target):
  threads.append(threading.Thread(target=target))
  threads[-1].daemon = True

def send(key, value):
  if options.verbose:
    sys.stderr.write("send %s : %s\n" % (key, value))
  sock.sendto(json.dumps((key, value)), (options.group, options.port))

def run():
  global options
  parser = optparse.OptionParser()
  parser.add_option("--daemonize", default=False, action="store_true", help="Daemonize the process.")
  parser.add_option("--group", default="224.1.1.1", help="Multicast group for sending source messages.  Default: %default")
  parser.add_option("--logfile", default=None, help="Log file.  Default: %default")
  parser.add_option("--pidfile", default=None, help="PID file.  Default: %default")
  parser.add_option("--port", type="int", default=5007, help="Multicast port for sending source messages.  Default: %default")
  parser.add_option("--uid", type="int", default=None, help="Drop privileges to uid.  Default: %default")
  parser.add_option("--ttl", type="int", default=1, help="Multicast TTL.  Default: %default")
  parser.add_option("--verbose", default=False, action="store_true",  help="Enable debugging output.")
  options, arguments = parser.parse_args()

  if options.verbose:
    for key in sorted(options.__dict__.keys()):
      sys.stderr.write("%s : %s\n" % (key, options.__dict__[key]))

  if options.daemonize:
    import daemon
    log = open(options.logfile, 'a+') if options.logfile is not None else sys.stderr
    context = daemon.DaemonContext(stdout=log, stderr=log,  working_directory='.')
    context.open()

  if options.uid is not None:
    os.setuid(options.uid)

  global sock
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, options.ttl)

  for thread in threads:
    thread.start()

  if options.pidfile:
    with open(options.pidfile, "wb") as pidfile:
      pidfile.write(str(os.getpid()))

  while True:
    try:
      time.sleep(1.0)
    except KeyboardInterrupt:
      break

  if options.pidfile:
    os.unlink(options.pidfile)
