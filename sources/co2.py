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
import re
import time
import urllib2
import xml.etree.ElementTree as xml

def co2(context):
  last_update = None
  data = None
  while True:
    now = datetime.datetime.utcnow()
    if last_update is None or now - last_update > datetime.timedelta(hours = 6):
      last_update = now

      rss = xml.fromstring(urllib2.urlopen("http://www.esrl.noaa.gov/gmd/webdata/ccgg/trends/rss.xml").read())
      timestamp = [element.text for element in rss.findall("./channel/item/guid")]
      values = [re.findall(r"(\d+\.\d*) (ppm)", element.text) for element in rss.findall("./channel/item/description")]
      data = {}
      for timestamp, values in zip(timestamp, values):
        if len(values) != 3:
          continue
        timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d")
        data[timestamp] = values[0]
        #data[timestamp - datetime.timedelta(weeks = 52)] = values[1]
        #data[timestamp - datetime.timedelta(weeks = 520)] = values[2]
      data = [(timestamp.strftime("%Y-%m-%d"), float(data[timestamp][0])) for timestamp in sorted(data.keys(), reverse=True)]

    context.send(data)
    time.sleep(10.0)

if __name__ == "__main__":
  artcast.source.add(
    co2,
    key="co2/maunaloa",
    description="Weekly average CO2 at the Mauna Loa observatory, in PPM.",
    provenance="Retrieved from NOAA at http://www.esrl.noaa.gov/gmd/webdata/ccgg/trends/rss.xml.",
    license={"uri" : "http://creativecommons.org/licenses/by-sa/3.0/", "title" : "CC BY-SA 3.0"}
    )
  artcast.source.run()

