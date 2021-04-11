from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
import sys
from time import sleep

leader = -1  # coordinator
address = 'localhost'
threads = {}
# live_list = {}
# crash_later = []
wait_ack = False


# global_buffer = ""

class ClientHandler(Thread):
    def __init__(self, index, addr: str, port: int):
        Thread.__init__(self)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((addr, port))
        self.buffer = []
        self.valid = True
        self.valid_since = 0

    def run(self):
        global global_buffer
        while self.valid:
            if len(self.buffer) > 0:
                sleep(.1)
                # print(f"working since: {self.valid_since}")
                self.valid_since = self.valid_since + 1
                print(f"Got your message: {self.buffer.pop(0)}")
                # self.buffer = []

            else:
                print("waiting...")
                sleep(1)
                try:
                    data = self.sock.recv(1024)
                    self.buffer.append(data.decode('utf-8'))
                except:
                    print(sys.exc_info())
                    self.valid = False
                    # del threads[self.index]
                    self.sock.close()
                    break

    def send(self, msg: str):
        if self.valid:
            self.sock.send(msg.encode('utf-8'))

    def close(self):
        try:
            self.valid = False
            self.sock.close()
        except:
            print(sys.exc_info())
            pass


if __name__ == "__main__":
    handler = ClientHandler(1, '', 8080)
    handler.start()
    while True:
        command = input("Give command:")
        if command == "stop":
            handler.close()
        else:
            handler.send(command)
    # handler.join()
