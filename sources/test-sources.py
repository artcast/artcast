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
import time

def tick(context):
  value = 0
  while True:
    context.send(value)
    value += 1
    time.sleep(1.0)

def now(context):
  while True:
    context.send(datetime.datetime.utcnow().isoformat())
    time.sleep(1.0)

if __name__ == "__main__":
  import artcast.source
  artcast.source.add(
    tick,
    key="test/tick",
    description="Monotonically increasing integer.",
    provenance="Local counter.",
    license={"uri" : "http://creativecommons.org/licenses/by-sa/3.0/", "title" : "CC BY-SA 3.0"}
    )
  artcast.source.add(
    now,
    key="test/now",
    description="Current UTC time in ISO-8601 format.",
    provenance="Python datetime.datetime.utcnow() function.",
    license={"uri" : "http://creativecommons.org/licenses/by-sa/3.0/", "title" : "CC BY-SA 3.0"}
    )
  artcast.source.run()
