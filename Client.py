import socket

def run_client(host, port, filename):
    # 1. 建立连接
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    # 2. 打开文件
    with open(filename, 'r') as f:
        # 3. for 每一行:
        for line in f:
            line = line.strip()  # 跳过空行
            if not line:
                continue  # 跳过空行
            # 发送
            sock.sendall(line.encode())
            # 接收
            response = sock.recv(1024).decode()
            # 打印
            print(response)
    # 4. 关闭连接
    sock.close()
    # 5. 关闭文件 (自动由 with 语句处理)
