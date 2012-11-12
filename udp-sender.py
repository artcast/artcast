import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for message in sys.argv[1:]:
  s.sendto(message, ("localhost", 51423))

