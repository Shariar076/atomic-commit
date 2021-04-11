import sys
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from res.globals import bcolors
import res.globals


class MasterHandler(Thread):
    def __init__(self, index, address, port):
        Thread.__init__(self)
        self.index = index
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((address, port))
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()
        self.valid = True

    def run(self):
        # conns[-1] = self.conn
        while True:
            try:
                data = self.conn.recv(1024).decode('utf-8')
                if data:
                    data = data.split('\n')
                    data = data[:-1]
                    for line in data:
                        res.globals.client.receive_master(line)
            except Exception as ex:
                print(f"{bcolors.FAIL}Exception in master_handler: {ex}{bcolors.ENDC}")
                print(sys.exc_info())
                # self.valid = False
                # del threads[self.index]
                self.sock.close()
                break

    def send_str(self, s):
        if self.valid:
            self.conn.send((str(s) + '\n').encode('utf-8'))

    def close(self):
        try:
            self.valid = False
            self.sock.close()
        except:
            pass
