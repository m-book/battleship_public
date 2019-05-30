import threading
import socket
from utility import *


class ConnectionThread(threading.Thread):
    def __init__(self, main):
        super(ConnectionThread, self).__init__()
        self.main = main
        self.host = ""
        self.port = 12345
        self.backlog = 10
        self.bufsize = 1024

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))

    def run(self):
        print(" === sub thread === ")
        self.sock.listen(self.backlog)
        conn, address = self.sock.accept()
        while True:
            mes = conn.recv(self.bufsize)
            user_id, status, data = receive_data(mes)
            self.main.received_data()

        self.sock.close()


class AcceptThread(threading.Thread):
    def __init__(self, main, port):
        super(AcceptThread, self).__init__()
        self.main = main
        self.host = ""
        self.port = port
        self.backlog = 10
        self.bufsize = 1024

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))

    def run(self):
        while True:
            self.sock.listen(self.backlog)
            conn, address = self.sock.accept()
            is_send_normal_user = True
            if self.main.user.is_host is True:
                is_send_normal_user = False
            self.main.init_listen_socket(conn, is_send_normal_user)


class ListenThread(threading.Thread):
    def __init__(self, conn, main):
        super(ListenThread, self).__init__()
        self.main = main
        self.conn = conn
        self.bufsize = 1024
        print('listen')

    def run(self):
        while True:
            mes = self.conn.recv(self.bufsize)
            user_id, status, data = receive_data(mes)
            self.main.received_data(user_id, status, data)
