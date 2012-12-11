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

import artcast.source
import datetime
import functools
import time

def poverty_death(offset, context):
  while True:
    timestamp = datetime.datetime.utcnow()
    timestamp = timestamp + offset
    midnight = datetime.datetime(timestamp.year, timestamp.month, timestamp.day)
    seconds = (timestamp - midnight).seconds

    deaths_per_second = 10500000.0 / 365.0 / 24.0 / 60.0 / 60.0
    context.send(int(seconds * deaths_per_second))
    time.sleep(1.0 / deaths_per_second)

def add_source(offset, label):
  artcast.source.add(
    functools.partial(poverty_death, offset),
    key="poverty/death/%s" % label,
    description="Worldwide deaths due to extreme poverty since midnight, %s." % label,
    provenance="Computed based on 10,500,000 deaths per year, as reported by everythreeseconds.net.",
    license={"uri" : "http://creativecommons.org/licenses/by-sa/3.0/", "title" : "CC BY-SA 3.0"}
    )

if __name__ == "__main__":
  add_source(datetime.timedelta(hours=-7), "UTC-0700")
  artcast.source.run()
