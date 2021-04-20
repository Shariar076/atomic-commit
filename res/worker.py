from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from res.globals import bcolors
from res.listener import Listener


class Worker(Thread):
    def __init__(self, address, internal_port):
        Thread.__init__(self)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind((address, internal_port))
        self.sock.listen(1)

    def run(self):
        while True:
            try:
                conn, addr = self.sock.accept()
                handler = Listener(conn, addr)
                handler.start()
            except Exception as ex:
                print(f"{bcolors.FAIL}Exception in worker: {ex}{bcolors.ENDC}")
                break

    def close(self):
        try:
            self.sock.close()
        except Exception as ex:
            print(f"{bcolors.FAIL}Worker Received Exception while closing socket : {ex}{bcolors.ENDC}")