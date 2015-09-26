import socket

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 8886)
    sock.connect(server_address)

    data = "TCP"
    length = len(data)
    ret = bytearray([])
    for byte in data.encode("utf-8"):
        ret.append(byte)
    sock.sendall(ret)

if __name__ == '__main__':
    main()
