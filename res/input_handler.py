import sys
from threading import Thread
import res.globals

class InputHandler(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            line = ''
            try:
                line = sys.stdin.readline()
            except:  # keyboard exception, such as Ctrl+C/D
                exit()
            if line == '':  # end of a file
                exit()
            line = line.strip()

            res.globals.client.inputs = line