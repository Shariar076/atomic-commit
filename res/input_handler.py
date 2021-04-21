import sys
from threading import Thread
import res.globals
from res.globals import bcolors


class InputHandler(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            line = ''
            try:
                line = sys.stdin.readline()
            except Exception as ex:  # keyboard exception, such as Ctrl+C/D
                print(f"{bcolors.FAIL}InputHandler Received Exception: {ex}{bcolors.ENDC}")
                # exit()

            line = line.rstrip()
            if line == 'playlist':
                res.globals.client.print_playlist()
            elif line == 'actions':
                res.globals.client.print_transactions()
            elif line == 'vetonext':
                print(f"{bcolors.WARNING}Process will vote No on the next vote-req.{bcolors.ENDC}")
                res.globals.client.flags['vetonext'] = True
            else:
                print(f"{bcolors.WARNING}Unrecognized command: {line}.{bcolors.ENDC}")