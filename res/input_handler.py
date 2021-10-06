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

            elif line == 'crashBeforeVote':
                print(f"{bcolors.WARNING}Process will crash before the next vote.{bcolors.ENDC}")
                res.globals.client.flags['crashBeforeVote'] = True
            elif line == 'crashAfterVote':
                print(f"{bcolors.WARNING}Process will crash after the next vote.{bcolors.ENDC}")
                res.globals.client.flags['crashAfterVote'] = True
            elif line == 'crashAfterAck':
                print(f"{bcolors.WARNING}Process will crash after the next ack.{bcolors.ENDC}")
                res.globals.client.flags['crashAfterAck'] = True

            elif line == 'crashVoteReq':
                print(f"{bcolors.WARNING}Cordinator will crash before the next vote-req.{bcolors.ENDC}")
                res.globals.client.flags['crashVoteReq'] = True
            elif line == 'crashPartialPreCommit':
                print(f"{bcolors.WARNING}Cordinator will crash before the next precommit.{bcolors.ENDC}")
                res.globals.client.flags['crashPartialPreCommit'] = True
            elif line == 'crashPartialCommit':
                print(f"{bcolors.WARNING}Cordinator will crash before the next commit.{bcolors.ENDC}")
                res.globals.client.flags['crashPartialCommit'] = True

            elif line == 'crash':
                print(f"{bcolors.WARNING}Process will crash immediately.{bcolors.ENDC}")
                res.globals.client.crash()
            else:
                print(f"{bcolors.WARNING}Unrecognized command: {line}.{bcolors.ENDC}")