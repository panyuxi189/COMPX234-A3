#READ(k)    读取 value（不删除）
#GET(k)     读取并删除
#PUT(k,v)   插入（key 不能重复）
import socket
import threading
import time

# 全局数据
tuple_space = {}
lock = threading.Lock()

# 统计信息
total_clients = 0
total_operations = 0
total_reads = 0
total_gets = 0
total_puts = 0
total_errors = 0

# NNN协议
def recv_full_message(conn):
    header = b''
    while len(header) < 3:
        more = conn.recv(3 - len(header))
        if not more:
            return None
        header += more

    total_length = int(header.decode())
    remaining = total_length - 3

    data = b''
    while len(data) < remaining:
        chunk = conn.recv(remaining - len(data))
        if not chunk:
            return None
        data += chunk

    return (header + data).decode()


# 构造响应（NNN）
def build_response(msg):
    length = len(msg) + 4
    return f"{length:03d} {msg}".encode()

def handle_client(client_socket):
    global total_clients, total_operations
    global total_reads, total_gets, total_puts, total_errors

    # 记录client
    with lock:
        total_clients += 1

    while True:
        # 接收客户端指令
        #参数1024：一次性最多接收 1024 字节 的数据（缓冲区大小）
        #返回值：二进制字节流（bytes 类型），不是字符串
        #把二进制字节流解码成字符串（str）
        #最后把干净的消息存入request变量
        
        # 协议读取
        request = recv_full_message(client_socket)
        if not request:
            break
         # 去掉NNN
        parts = request[4:].strip().split()
        if not parts:
            continue

        command = parts[0]
        if command in ["R", "G"] and len(parts) < 2:
            client_socket.sendall(build_response("ERR invalid command"))
            continue

        if command == "P" and len(parts) < 3:
            client_socket.sendall(build_response("ERR invalid command"))
            continue

        with lock:
            total_operations += 1

            # READ
            if command == "R":
                total_reads += 1
                key = parts[1]

                if key in tuple_space:
                    value = tuple_space[key]
                    response = build_response(f"OK ({key}, {value}) read")
                else:
                    total_errors += 1
                    response = build_response(f"ERR {key} does not exist")

            #  GET 
            elif command == "G":
                total_gets += 1
                key = parts[1]

                if key in tuple_space:
                    value = tuple_space.pop(key)
                    response = build_response(f"OK ({key}, {value}) removed")
                else:
                    total_errors += 1
                    response = build_response(f"ERR {key} does not exist")

            # PUT 
            elif command == "P":
                total_puts += 1
                key = parts[1]
                value = " ".join(parts[2:])  # 支持空格

                if key in tuple_space:
                    total_errors += 1
                    response = build_response(f"ERR {key} already exists")
                else:
                    tuple_space[key] = value
                    response = build_response(f"OK ({key}, {value}) added")

            # ================= 错误命令 =================
            else:
                total_errors += 1
                response = build_response("ERR invalid command")

        client_socket.sendall(response)

    client_socket.close()


# 统计线程
def stats_printer():
    while True:
        time.sleep(10)

        with lock:
            n = len(tuple_space)

            if n == 0:
                avg_tuple = avg_key = avg_val = 0
            else:
                total_key_len = sum(len(k) for k in tuple_space)
                total_val_len = sum(len(v) for v in tuple_space.values())

                avg_key = total_key_len / n
                avg_val = total_val_len / n
                avg_tuple = (total_key_len + total_val_len) / n

            print("\n--- Server Stats ---")
            print(f"Tuples: {n}")
            print(f"Avg tuple size: {avg_tuple:.2f}")
            print(f"Avg key size: {avg_key:.2f}")
            print(f"Avg value size: {avg_val:.2f}")
            print(f"Clients: {total_clients}")
            print(f"Operations: {total_operations}")
            print(f"READ: {total_reads} GET: {total_gets} PUT: {total_puts}")
            print(f"Errors: {total_errors}")
            print("---------------------\n")


# 主程序 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 9090))
server_socket.listen()

print("Server running on port 9090")

# 启动统计线程
threading.Thread(target=stats_printer, daemon=True).start()

while True:
    client_socket, addr = server_socket.accept()

    # 多线程
    thread = threading.Thread(target=handle_client, args=(client_socket,))
    thread.start()

