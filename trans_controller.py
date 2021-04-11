import sys, os, subprocess, re
from socket import socket, AF_INET, SOCK_STREAM
import res.globals
from res.input_handler import InputHandler
from res.master_handler import MasterHandler
from res.timeout import Timeout
from res.worker import Worker
from trans_manager import Client
from res.globals import bcolors


# def send_str(p_id, data):
#     if p_id == -1:
#         res.globals.outgoing_conns[p_id].send_str(data)
#         return True
#
#     try:
#         sock = socket(AF_INET, SOCK_STREAM)
#         sock.connect((res.globals.address, res.globals.root_port + p_id))
#         sock.send((str(data) + '\n').encode('utf-8'))
#         sock.close()
#     except:
#         return False
#     return True
def kill_ps_on_port(port):
    command = "lsof -i :%s | awk '{print $2}'" % port
    pids = subprocess.check_output(command, shell=True)
    pids = pids.strip()
    if pids:
        pids = re.sub(' +', ' ', pids)
        for pid in pids.split('\n'):
            try:
                command = f'kill -9 {pid}'
                os.system(command)
            except:
                pass


def send_many(p_id_list, data):
    print(f'{bcolors.OKCYAN}send_many being called by {str(p_id_list)}{bcolors.ENDC}')
    true_list = []
    for p_id in p_id_list:
        print(f'{bcolors.OKCYAN}sending to {p_id}{bcolors.ENDC}')
        if p_id == -1:
            res.globals.outgoing_conns[p_id].send_str(data)
            true_list.append(p_id)
            continue
        # if p_id == my_pid:
        #  true_list.append(p_id)
        #  client.receive(data)
        #  continue

        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((res.globals.address, res.globals.root_port + p_id))
            sock.send((str(data) + '\n').encode('utf-8'))
            sock.close()
        except:
            continue
        true_list.append(p_id)
    return true_list


def main():
    print(sys.argv)
    pid = int(sys.argv[1])
    # my_pid = pid
    num_processes = int(sys.argv[2])
    myport = int(sys.argv[3])

    # Timeouts
    coordinator_timeout_vote_req = Timeout(res.globals.timeout_wait, 'coordinator-vote-req')
    coordinator_timeout_precommit = Timeout(res.globals.timeout_wait, 'coordinator-precommit')
    coordinator_timeout_commit = Timeout(res.globals.timeout_wait, 'coordinator-commit')
    process_timeout_vote = Timeout(res.globals.timeout_wait, 'process-vote')
    process_timeout_acks = Timeout(res.globals.timeout_wait, 'process-acks')
    coordinator_timeout_vote_req.start()
    coordinator_timeout_precommit.start()
    coordinator_timeout_commit.start()
    process_timeout_vote.start()
    process_timeout_acks.start()

    # Connection with MASTER
    kill_ps_on_port(myport)
    mhandler = MasterHandler(pid, res.globals.address, myport)
    res.globals.outgoing_conns[-1] = mhandler

    # All incoming connections
    # kill_ps_on_port(res.globals.root_port + pid)
    handler = Worker(res.globals.address, res.globals.root_port + pid)
    handler.start()

    # All outgoing connections
    ##  for pno in range(num_processes):
    ##    if pno == pid:
    ##      continue
    ##    handler = ClientHandler(pno, address, root_port+pno)
    ##    outgoing_conns[pno] = handler
    ##    handler.start()

    res.globals.client = Client(pid, num_processes, send_many, coordinator_timeout_vote_req,
                                coordinator_timeout_precommit, coordinator_timeout_commit, process_timeout_vote,
                                process_timeout_acks)
    print(f"{bcolors.OKCYAN}Client has been inited{bcolors.ENDC}")
    res.globals.client.load_state()
    mhandler.start()
    input_handler = InputHandler()
    input_handler.start()
    coordinator_timeout_vote_req.restart()

    while True:
        a = 1


if __name__ == '__main__':
    main()
