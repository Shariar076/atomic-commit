import time
from threading import Thread
import res.globals
from res.globals import bcolors

class Timeout(Thread):
    def __init__(self, timeout, waiting_on):
        Thread.__init__(self)
        self.timeout = timeout
        self.waiting_on = waiting_on
        self.__is__running = True
        self.__suspend__ = True

    def run(self):
        while self.__is__running:
            if not self.__suspend__:
                time.sleep(0.5)
                self.timeout -= 0.5

                if self.timeout <= 0:
                    if self.waiting_on == 'coordinator-vote-req':
                        print(f'{bcolors.HEADER}Timed out waiting for vote-req{bcolors.ENDC}')
                        # Run re-election protocol
                        self.suspend()
                        res.globals.client.re_election_protocol()
                        self.timeout = res.globals.timeout_wait

                    elif self.waiting_on == 'coordinator-precommit':
                        print(f'{bcolors.HEADER}Timed out waiting for precommit{bcolors.ENDC}')
                        self.suspend()
                        # Run Termination protocol
                        self.timeout = res.globals.timeout_wait

                    elif self.waiting_on == 'process-vote':
                        self.suspend()
                        print(f'{bcolors.HEADER}Timed out waiting for votes{bcolors.ENDC}')
                        # Send abort to all

                    elif self.waiting_on == 'process-acks':
                        self.suspend()
                        print(f'{bcolors.HEADER}Timed out waiting for acks{bcolors.ENDC}')
                        # Send Commits to remaining processes
                        res.globals.client.after_timed_out_on_acks()

                    elif self.waiting_on == 'coordinator-commit':
                        self.suspend()
                        print(f'{bcolors.HEADER}Timed out waiting for commit{bcolors.ENDC}')
                        # Termination protocol

    def reset(self):
        print(f'{bcolors.HEADER}Time out set on {self.waiting_on} for {self.timeout}s{bcolors.ENDC}')
        self.timeout = res.globals.timeout_wait

    def restart(self):
        self.reset()
        self.__suspend__ = False

    def suspend(self):
        self.__suspend__ = True

    def stop(self):
        self.__is__running = False
