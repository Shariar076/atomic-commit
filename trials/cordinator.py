import sys
from socket import socket, AF_INET, SOCK_STREAM

from master_handler import MasterHandler
from timeout_thread import TimeoutThread
from worker_thread import WorkerThread
from process import Client

import globals


def send_many(p_id_list, data):
    print('send_many being called by ' + str(p_id_list))
    # global root_port, outgoing_conns, address, my_pid
    true_list = []
    for p_id in p_id_list:
        if p_id == -1:
            globals.outgoing_conns[p_id].send(str(data) + '\n')
            true_list.append(p_id)
            continue
        # if p_id == my_pid:
        #  true_list.append(p_id)
        #  client.receive(data)
        #  continue

        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((globals.address, globals.root_port + p_id))
            sock.send(str(data) + '\n')
            sock.close()
        except:
            continue
        true_list.append(p_id)
    return true_list


def main():
    # global address, client, root_port, processes, outgoing_conns

    # print(sys.argv)
    pid = int(sys.argv[1])
    # my_pid = pid
    num_processes = int(sys.argv[2])
    own_port = int(sys.argv[3])

    print(f"Got pid:{pid}, num_processes:{num_processes}, my port:{own_port}")

    # Timeouts

    coordinator_timeout_vote_req = TimeoutThread('coordinator-vote-req')
    coordinator_timeout_vote_req.start()
    print("timeout_thead started")

    m_handler = MasterHandler(pid, globals.address, own_port)
    globals.outgoing_conns[0] = m_handler

    # All incoming connections
    handler = WorkerThread(globals.address, globals.root_port + pid)
    handler.start()
    print("worker_thead started")

    globals.client = Client(pid, num_processes, send_many, coordinator_timeout_vote_req)
    print("Client has been inited")
    globals.client.load_state()
    m_handler.start()
    print("master_thead started")

    coordinator_timeout_vote_req.restart()


if __name__ == '__main__':
    main()
