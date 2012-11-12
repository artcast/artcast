import json
import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(json.dumps((sys.argv[1], sys.argv[2])), ("localhost", 51423))

