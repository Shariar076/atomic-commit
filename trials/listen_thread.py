from threading import Thread
import globals


class ListenThread(Thread):
    def __init__(self, conn, addr):
        Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    # From Daniel
    def run(self):
        # global client
        while True:
            try:
                data = self.conn.recv(1024)
                if data != "":
                    data = data.split('\n')
                    data = data[:-1]
                    for line in data:
                        # print "process - Inside loop - " + str(line)
                        globals.client.receive(line)

            except:
                break
