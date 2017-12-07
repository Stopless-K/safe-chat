import socket, threading, time, queue
encoding = 'utf-8'

class Result:
    connect_success = bytes('1', encoding)
    send_success = bytes('2', encoding)

def str_to_byte(x):
    return bytes(x, encoding)

def byte_to_str(x):
    return x.decode(encoding)

def no_checking(username, password):
    if password == '123456':
        return username
    return None

class Server(object):
    def __init__(self, port=23333, encode=str_to_byte, decode=byte_to_str, check_user=no_checking):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', port))
        print('[RUN] port: {}'.format(port))
        self.socket.listen(5)
        self.result = Result()
        self.decode = decode
        self.encode = encode
        self.login_queue = queue.Queue()
        self.check_user = check_user
        self.online_dict = {}
        self.sending_queue = queue.Queue()

    def login(self, sock):
        sock.send(self.encode('--! username'))
        username = self.decode(sock.recv(1024))
        sock.send(self.encode('--! password'))
        password = self.decode(sock.recv(1024))
        return self.check_user(username, password)

    def anaylize(self, data, user):
        if data[:4] == '--! ':
            print('[RUN] order mode ..')
            data = data[4:].split(' ')
            if data[0] == 'to':
                self.online_dict[user]['chat_to'] = data[1]
                print('[RUN] {} is talking to {} ..'.format(user, data[1]))
        else:
            chat_to = self.online_dict[user]['chat_to']
            # print('[RUN] {} are sending to {}'.format(user, chat_to))
            # print('[LOG] online users: {}'.format(self.online_dict))
            if chat_to in self.online_dict and chat_to != user:
                self.sending_queue.put([
                    self.online_dict[chat_to]['sock'],
                    self.encode(user + ': ' + data),
                ])
                return None
            else:
                return '[ERR] {} is not online!'.format(chat_to)
        
        return None

        
    def send(self, sock, data):
        sock.send(data)
        return True
        # return sock.recv(1024) == send_success

    def auto_send(self):
        print('[RUN] auto_send started ..')
        while True:
            sock, data = self.sending_queue.get()
            # print('[RUN] data got! sending ..')
            while not self.send(sock, data):
                # print('[ERR] send failed, resending ..')
                pass

    def tcplink(self, sock, addr):
        print('[LIN] address: {}'.format(addr))
        sock.send(self.result.connect_success)
        user = self.login(sock)
        if not user:
            res = '[END] login failed ..'
            sock.send(self.encode(res))
            return
        sock.send(self.encode('[SUC] login successfully!'))

        self.online_dict[user] = {'sock': sock, 'addr': addr, 'chat_to': '----', 'username': user}

        while True:
            data = self.decode(sock.recv(1024))
            if not data:
                break
            # print('[GET] data: {}'.format(data))
            res = self.anaylize(data, user)
            # print('[RUN] add to sending_queue ..')
            if res:
                sock.send(self.encode(res))
            # print('[SUC] added ..')
        sock.close()
        print('[END] connection from {} closed ..'.format(addr))
        
    def run(self):
        q = []
        t = threading.Thread(target=self.auto_send, args=())
        t.start()
        q.append(t)
        while True:
            print('[RUN] server is running now, waiting for new client ..')
            sock, addr = self.socket.accept()

            t = threading.Thread(target=self.tcplink, args=(sock, addr,))
            t.start()
            q.append(t)

        for t in q:
            t.join()


if __name__ == '__main__':
    server = Server()
    server.run()
