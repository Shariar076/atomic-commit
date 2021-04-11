import sys
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from globals import client
from listen_thread import ListenThread


class WorkerThread(Thread):
    def __init__(self, address, internal_port):
        Thread.__init__(self)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((address, internal_port))
        self.sock.listen(1)

    def run(self):
        while True:
            conn, addr = self.sock.accept()
            handler = ListenThread(conn, addr)
            handler.start()