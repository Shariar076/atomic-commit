import sys
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

import globals


class MasterHandler(Thread):
    def __init__(self, index, address, port):
        Thread.__init__(self)

        self.index = index
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((address, port))
        self.sock.listen(1)
        # self.conn, self.addr = self.sock.accept()
        self.valid = True

    def run(self):
        # global client, conns, threads
        # conns[-1] = self.conn
        self.conn, self.addr = self.sock.accept()
        while True:
            try:
                data = self.conn.recv(1024)
                if data:
                    data = data.split('\n')
                    data = data[:-1]
                    for line in data:
                        globals.client.receive_master(line)
            except:
                print(sys.exc_info())
                # self.valid = False
                # del threads[self.index]
                self.sock.close()
                break

    def send(self, s):
        if self.valid:
            self.conn.send(str(s) + '\n')

    def close(self):
        try:
            self.valid = False
            self.sock.close()
        except:
            pass