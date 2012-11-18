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

if __name__ == "__main__":
  import artcast.source
  artcast.source.parse()
  artcast.source.register(key=artcast.source.arguments[0], description="Command-line source.", provenance="Command line value.")
  artcast.source.send(key=artcast.source.arguments[0], value=artcast.source.arguments[1])
