#READ(k)    读取 value（不删除）
#GET(k)     读取并删除
#PUT(k,v)   插入（key 不能重复）
import socket
import threading

tuple_space = {}

def handle_client(client_socket):
    while True:
        # 接收客户端指令
        #参数1024：一次性最多接收 1024 字节 的数据（缓冲区大小）
        #返回值：二进制字节流（bytes 类型），不是字符串
        #把二进制字节流解码成字符串（str）
        #最后把干净的消息存入request变量
        request = client_socket.recv(1024).decode()
        if not request:
            break
        
        # 拆分命令和参数
        command, *args = request.split() #去除字符串首尾的空白字符：空格、换行\n、回车\r、制表符\t
        
        if command == "READ":
            key = args[0] # 取出客户端要查询的 key
            value = tuple_space.get(key, "NULL")  # 从元组空间取值，不存在返回 NULL
            client_socket.send(value.encode())     # 把结果发回客户端
        
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