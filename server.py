import socket, threading, time
encoding = 'utf-8'

class Result:
    connect_success = bytes('1', encoding)
    send_success = bytes('2', encoding)

def str_to_byte(x):
    return bytes(x, encoding)

def byte_to_str(x):
    return x.decode(encoding)

class Server(object):
    def __init__(self, port=23333, encode=str_to_byte, decode=byte_to_str):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', port))
        self.socket.listen(5)
        self.result = Result()
        self.decode = decode
        self.encode = encode

    def tcplink(self, sock, addr):
        print('[LIN] address: {}'.format(addr))
        sock.send(self.result.connect_success)
        while True:
            data = sock.recv(1024)
            sock.send(self.result.send_success)
            if not data:
                break
            print('[GET] data: {}'.format(self.decode(data)))
        sock.close()
        print('[END] connection from {} closed ..'.format(addr))
        
    def run(self):
        sock, addr = self.socket.accept()
        t = threading.Thread(target=self.tcplink(sock, addr))


if __name__ == '__main__':
    server = Server()
    server.run()
