import subprocess
import sys, os
import time
from socket import socket, AF_INET, SOCK_STREAM
import signal
import res.globals
from res.globals import bcolors
from res.input_handler import InputHandler
from res.master_handler import MasterHandler
from res.timeout import Timeout
from res.worker import Worker
from trans_manager import Client


def kill_ps_on_port(port):
    command = f"lsof -t -i tcp:{port} | xargs kill -9"
    try:
        subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def send_many(p_id_list, data):
    print(f'{bcolors.OKCYAN}Send_many being called by {str(p_id_list)}{bcolors.ENDC}')
    true_list = []
    for p_id in p_id_list:
        print(f'{bcolors.OKCYAN}Sending to {p_id}{bcolors.ENDC}')
        if p_id == -1:
            res.globals.outgoing_conns[p_id].send_str(data)
            true_list.append(p_id)
            continue

        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((res.globals.address, res.globals.root_port + p_id))
            sock.send((str(data) + '\n').encode('utf-8'))
            sock.close()
        except Exception as ex:
            # print(f"{bcolors.FAIL}Controller Received Exception at send_many: {ex}{bcolors.ENDC}")
            continue
        true_list.append(p_id)
    return true_list


def main():
    print(sys.argv)
    pid = int(sys.argv[1])
    num_processes = int(sys.argv[2])
    myport = int(sys.argv[3])

    input_handler = InputHandler()
    process_timeout_vote = Timeout(res.globals.timeout_wait, 'process-vote')
    process_timeout_acks = Timeout(res.globals.timeout_wait, 'process-acks')
    process_timeout_vote.start()
    process_timeout_acks.start()

    try:
        mhandler = MasterHandler(pid, res.globals.address, myport)
    except Exception as ex:
        print(f"{bcolors.FAIL}Exception starting master handler: {ex}{bcolors.ENDC}")
    res.globals.outgoing_conns[-1] = mhandler

    # All incoming connections

    worker = Worker(res.globals.address, res.globals.root_port + pid)

    input_handler.start()
    worker.start()

    res.globals.client = Client(pid, num_processes, send_many, process_timeout_vote, process_timeout_acks)
    print(f"{bcolors.OKCYAN}Client has been inited{bcolors.ENDC}")
    res.globals.client.load_state()

    mhandler.start()

    def keyboard_interrupt_handler(signal, frame):
        print(f"{bcolors.OKCYAN}KeyboardInterrupt (ID: {format(signal)}) has been caught. Cleaning up...{bcolors.ENDC}")
        mhandler.close()
        worker.close()
        # worker.join()
        # mhandler.join()
        os._exit(0)

    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    time.sleep(100)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print(f"{bcolors.FAIL}Controller Received Exception: {ex}{bcolors.ENDC}")
