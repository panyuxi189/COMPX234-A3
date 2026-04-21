import socket

s.socket.socket()
s.connect(("localhost", 9090))

s.sendall("PUT a 1".encode())
print(s.recv(1024).decode())