#READ(k)    读取 value（不删除）
#GET(k)     读取并删除
#PUT(k,v)   插入（key 不能重复）
import socket

tuple_space = {}

def handle_client(client_socket):
    while True:
        request = client_socket.recv(1024).decode()
        if not request:
            break
        
        command, *args = request.split()
        
        if command == "READ":
            key = args[0]
            value = tuple_space.get(key, "NULL")
            client_socket.send(value.encode())
        
        elif command == "GET":
            key = args[0]
            value = tuple_space.pop(key, "NULL")
            client_socket.send(value.encode())
        
        elif command == "PUT":
            key, value = args
            if key in tuple_space:
                client_socket.send("ERROR: Key already exists".encode())
            else:
                tuple_space[key] = value
                client_socket.send("OK".encode())
    
    client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)