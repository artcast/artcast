import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto("Hello!", ("localhost", 51423))

