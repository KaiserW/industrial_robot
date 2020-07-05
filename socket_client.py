import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.125.2', 8080))

while True:
    query = input(">>> Query Code: ")
    s.send(query.encode())

    if query == '02':
        data = s.recv(1024)
        print(repr(data))

    if query == '03':
        break

s.close()

