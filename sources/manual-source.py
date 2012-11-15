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
import socket
import sys

parser = optparse.OptionParser()
parser.add_option("--group", default="224.1.1.1", help="Multicast group for sending source messages.  Default: %default")
parser.add_option("--port", type="int", default=5007, help="Multicast port for sending source messages.  Default: %default")
parser.add_option("--ttl", type="int", default=1, help="Multicast TTL.  Default: %default")
parser.add_option("--verbose", default=False, action="store_true",  help="Enable debugging output.")
options, arguments = parser.parse_args()

if options.verbose:
  for key in sorted(options.__dict__.keys()):
    sys.stderr.write("%s : %s\n" % (key, options.__dict__[key]))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, options.ttl)
sock.sendto(json.dumps((sys.argv[1], sys.argv[2])), (options.group, options.port))

