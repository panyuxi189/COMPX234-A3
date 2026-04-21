import socket
import threading
import sys

def build_message(line):
    """
    把一行指令转换成带 NNN 的协议格式
    """
    msg_body = line.strip()
    msg_body = line.strip()
    length = len(msg_body) + 4  # 3字节长度 + 1空格
    
    full_msg = f"{length:03d} {msg_body}"
    return full_msg.encode()


def recv_full_message(sock):
    """
    按照协议接收完整消息
    """
    # 1. 先收3字节（NNN）
    header = sock.recv(3)
    if not header:
        return None
    
    total_length = int(header.decode())
    
    # 2. 还需要读取多少
    remaining = total_length - 3
    
    data = b''
    while len(data) < remaining:
        chunk = sock.recv(remaining - len(data))
        if not chunk:
            break
        data += chunk
    
    return (header + data).decode()


def is_valid_put(line):
    """
    检查 PUT 是否满足长度限制（970）
    """
    parts = line.split()
    if parts[0] != "PUT":
        return True
    
    if len(parts) < 3:
        return False
    
    key = parts[1]
    value = " ".join(parts[2:])
    
    return len(key + value) <= 970
def run_client(host, port, filename):
    # 1. 建立连接
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    # 2. 打开文件
        with open(filename, 'r') as f:
        # 3. for 每一行:
            for line in f:
                line = line.strip()  # 跳过空行
                if not line:
                    continue  # 跳过空行
                # 检查 PUT 长度
                if not is_valid_put(line):
                    print(f"{line}: ERR input too long")
                    continue
                # 构造消息
                msg = build_message(line)
                # 发送
                sock.sendall(msg)
                # 接收响应
                response = sock.recv(1024).decode()
                if response is None:
                    print("Server disconnected")
                    break
                # 打印
                print(response)
        # 4. 关闭连接
        sock.close()
    # 5. 关闭文件 (自动由 with 语句处理)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py <host> <port> <file>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]
    
    run_client(host, port, filename)