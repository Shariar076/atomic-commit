import time
from threading import Thread
import globals


class TimeoutThread(Thread):
    def __init__(self, waiting_on):
        Thread.__init__(self)
        self.timeout_clock = globals.timeout_wait
        self.waiting_on = waiting_on
        self.__is__running = True
        self.__suspend__ = True

    def run(self):

        while self.__is__running:
            if not self.__suspend__:
                time.sleep(0.5)
                self.timeout_clock -= 0.5

                if self.timeout_clock <= 0:
                    if self.waiting_on == 'coordinator-vote-req':
                        print('coordinator-vote-req')
                        self.suspend()
                        break

    def reset(self):
        self.timeout_clock = globals.timeout_wait

    def restart(self):
        self.reset()
        self.__suspend__ = False

    def suspend(self):
        self.__suspend__ = True

    def stop(self):
        self.__is__running = False
