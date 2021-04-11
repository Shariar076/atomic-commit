from threading import Thread
import res.globals

class Listener(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        while True:
            try:
                data = self.conn.recv(1024).decode('utf-8')
                if data != "":
                    data = data.split('\n')
                    data = data[:-1]
                    for line in data:
                        res.globals.client.receive(line)

            except:
                break
