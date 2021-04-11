import socket


class Client:

    def __init__(self):
        self.socket = socket.socket()

    def connect_server(self, host, port):
        self.socket.connect((host, port))

    def send_msg(self, msg: str):
        socket.send(msg.encode('utf-8'))

    def recv_msg(self):
        return socket.recv(1024).decode('utf-8')

    def close_client(self):
        self.socket.close()
