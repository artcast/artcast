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

import time
import artcast

def tick():
  value = 0
  while True:
    artcast.send("test/tick", value)
    value += 1
    time.sleep(1.0)

def now():
  import datetime
  while True:
    artcast.send("test/now", datetime.datetime.utcnow().isoformat())
    time.sleep(1.0)

if __name__ == "__main__":
  artcast.add(tick)
  artcast.add(now)
  artcast.run()
