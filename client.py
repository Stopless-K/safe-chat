import socket, threading
from IPython import embed

encoding = 'utf-8'

class Result:
    connect_success = bytes('1', encoding)
    send_success = bytes('2', encoding)

def str_to_byte(x):
    return bytes(x, encoding)

def byte_to_str(x):
    return x.decode(encoding)

class Client(object):
    def __init__(self, ip='127.0.0.1', port=23333, history_size=100, encode=str_to_byte, decode=byte_to_str):
        print('[RUN] connecting to {}:{} ..'.format(ip, port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.decode = decode
        self.encode = encode
        self.result = Result()
        res = self.socket.recv(1024)
        if res == self.result.connect_success:
            print('[SUC] {}:{} connected ..'.format(ip, port))
            
            data = self.socket.recv(1024)
            assert self.decode(data) == '--! username'
            username = input('username: ')
            self.socket.send(self.encode(username))
            
            data = self.socket.recv(1024)
            assert self.decode(data) == '--! password'
            password = input('password: ')
            self.socket.send(self.encode(password))

            res = self.decode(self.socket.recv(1024))
            print(res)
            if res[1:4] == 'END':
                self.status = 'fail'
            else:
                self.status = 'success'
        else:
            print('[ERR] connecting to {}:{} failed ..'.format(ip, port))
            self.status = 'fail'
        self.history = [''] * history_size
        self.history_size = history_size
        self.history_pointer = 0
        self.cnt = 0

    def auto_receive(self):
        while True:
            data = self.decode(self.socket.recv(1024))
            if not data:
                break
            print(data)


    def send(self, s, resend=False):
        self.socket.send(self.encode(s))

        return True
        if not resend:
            self.history[self.history_pointer] = 1
            self.history_pointer = (self.history_pointer + 1) % self.history_size
            self.cnt = min(self.cnt + 1, self.history_size)


        if self.socket.recv(1024) == self.result.send_success:
            print('[SUC] {} sent ..'.format(s))
            return True
        else:
            print('[ERR] sending {} failed ..'.format(s))
            return False
            

    def resend(self, index = -1):
        if len(self.cnt) == 0:
            print('[WRN] no history ..')
            return False
        assert type(index) == type(int)
        index %= cnt
        return self.send(self.history[
            ((self.history_pointer+index) % self.history_size if cnt == history_size or index < 0 else index)
        ], resend=True)

    def free_style(self):
        t = threading.Thread(target=self.auto_receive, args=())
        t.start()
        while True:
            # data = input3('order: ')
            data = input()
            self.send(data)
        t.join()


    def __del__(self):
        pass

if __name__ == '__main__':
    # try:
    #     with open('./server.txt', 'r') as f:
    #         ip, port = f.read().split(' ')
    #     port = int(port)
    #     client = Client(ip, port)
    # except:
    #     client = Client()
    client = Client()
    if client.status == 'fail':
        client = None
    client.free_style()

    


