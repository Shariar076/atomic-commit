import socket


class Server:
    def __init__(self, host: str, port: int):
        self.socket = socket.socket()
        self.socket.bind((host, port))
        print("socket binded to %s" % (port))
        self.socket.listen(5)
        self.clients = []

    def start_server(self):
        print("Starting server")
        while True:
            # Establish connection with client.
            client, addr = self.socket.accept()
            print('Got connection from', addr)
            self.clients.append(client)
            # client.send('Thank you for connecting'.encode('utf-8'))
            # client.close()

    def send_msg(self, client: socket, msg: str):
        client.send(msg.encode('utf-8'))

    def recv_msg(self, client: socket):
        return client.recv(1024).decode('utf-8')

    def close_client(self, client: socket):
        client.close()

    def close_server(self):
        self.socket.close()
