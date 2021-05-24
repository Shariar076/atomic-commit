import json
import os
import threading
from copy import copy
from pprint import pprint
import res
from res.globals import bcolors
from socket import socket, AF_INET, SOCK_STREAM


class Client:
    def __init__(self, pid, num_procs, p_t_vote, p_t_acks, c_t_vote_req, c_t_prec, c_t_commit):
        self.alive = [pid]
        self.stupid = False
        self.coordinator = None
        self.data = {}
        self.flags = {}
        self.id = pid
        self.lock = threading.Lock()
        self.logfile = '%dlog.p' % pid
        self.message = 'state-req'
        self.N = num_procs
        # self.send = send
        self.transaction = {'number': 0,
                            'song': None,
                            'state': 'committed',
                            'action': None,
                            'URL': None}
        self.transaction_list = []
        self.num_messages_received_for_election = 0
        self.p_t_vote = p_t_vote
        self.p_t_acks = p_t_acks

        self.c_t_vote_req = c_t_vote_req
        self.c_t_prec = c_t_prec
        self.c_t_commit = c_t_commit
        self.election_alive_list = [pid]

    def send_data(self, p_id_list, data):
        print(f'{bcolors.OKCYAN}Send data being called by {str(p_id_list)}{bcolors.ENDC}')
        true_list = []
        for p_id in p_id_list:
            print(f'{bcolors.OKCYAN}Sending to {p_id}{bcolors.ENDC}')
            if p_id == -1:
                res.globals.outgoing_conns[p_id].send_str(data)
                true_list.append(p_id)

            else:
                try:
                    sock = socket(AF_INET, SOCK_STREAM)
                    sock.connect((res.globals.address, res.globals.root_port + p_id))
                    sock.send((str(data) + '\n').encode('utf-8'))
                    sock.close()
                except Exception as ex:
                    # print(f"{bcolors.FAIL}Received Exception at send_data: {ex}{bcolors.ENDC}")
                    continue
                true_list.append(p_id)
        return true_list

    def after_timed_out_on_acks(self):
        with self.lock:
            self.message = 'commit'
            self.send_data(self.alive, self.message_str())
            self.log()

    def re_election_protocol(self):
        with self.lock:
            print(f'{bcolors.OKGREEN}Starting re-election{bcolors.ENDC}')
            self.num_messages_received_for_election = 0
            self.message = 're-elect-coordinator'
            self.election_alive_list = self.broadcast()
            print(f'{bcolors.OKGREEN}alive list: {self.alive}{bcolors.ENDC}')
            print(f'{bcolors.OKGREEN}Got election alive list: {self.election_alive_list}{bcolors.ENDC}')
            # for p in self.alive:
            #     if p not in self.election_alive_list:
            #         print(f"p{p} is dead")
            #         self.alive.remove(p)
            self.alive = copy(self.election_alive_list)
            print(f'{bcolors.OKGREEN}Updated alive list: {self.alive}{bcolors.ENDC}')

    def after_timed_out_on_vote(self):
        with self.lock:
            self.message = 'abort'
            self.send_data(self.alive, self.message_str())
            self.log()

    def simple_dict(self):
        return {'alive': self.alive,
                'coordinator': self.coordinator,
                'data': self.data,
                'flags': self.flags,
                'id': self.id,
                'message': self.message,
                'transaction': self.transaction}

    def message_str(self):
        to_send = self.simple_dict()
        result = json.dumps(to_send)
        return result

    def broadcast(self):
        recipients = range(self.N)  # PID of all processes.
        message = self.message_str()  # Serialize self.
        return self.send_data(recipients, message)

    def load_state(self):
        print(f'{bcolors.OKGREEN}Process {self.id} alive for the first time{bcolors.ENDC}')
        self.c_t_vote_req.restart()
        self.alive = self.broadcast()
        if len(self.alive) == 1:
            self.coordinator = self.id
            self.send_data([-1], f'coordinator {self.id}')

    def log(self):
        pass

    def crash(self):
        print("Crashing ...")
        os._exit(1)

    def print_playlist(self):
        print(f'{bcolors.OKGREEN}Current playlist of pid {self.id}: {self.data}{bcolors.ENDC}')

    def print_transactions(self):
        print(f'{bcolors.OKGREEN}Current transactions by pid {self.id}:')
        for trans in self.transaction_list:
            print(json.dumps(trans, indent=4))
        print(bcolors.ENDC)
        
    def receive_master(self, s):
        with self.lock:
            print(f'{bcolors.OKGREEN}Received from master: {str(s)}{bcolors.ENDC}')
            parts = s.split()
            if parts[0] in ['add', 'edit', 'delete']:
                # start the vote_req_timout here maybe?? no
                if self.coordinator == self.id:
                    self.transaction = {'number': self.transaction['number'] + 1,
                                        'song': parts[1],
                                        'state': 'uncertain',
                                        'action': parts[0],
                                        'URL': parts[2] if parts[0] in ['add', 'edit'] else None}
                    self.message = 'vote-req'
                    self.acks = {}
                    self.votes = {}
                    if 'crashVoteReq' in self.flags:
                        # self.send_data(self.flags['crashVoteReq'], self.message_str())
                        del self.flags['crashVoteReq']
                        self.log()
                        self.crash()
                    else:
                        self.alive = self.broadcast()
                        print(f'{bcolors.OKGREEN}Self alive = {self.alive}{bcolors.ENDC}')
                        self.log()
                        self.p_t_vote.restart()
                else:
                    self.send_data([-1], 'ack abort')
            elif parts[0] == 'crash':
                self.crash()

            elif parts[0] == 'get':
                if parts[1] in self.data:
                    url = self.data[parts[1]]
                    self.send_data([-1], 'resp ' + url)
                else:
                    self.send_data([-1], 'resp NONE')
            # elif parts[0] == 'vote' and parts[1] == 'NO':
            #     self.flags['vote NO'] = True
        print(f'{bcolors.OKGREEN}End receive_master{bcolors.ENDC}')

    def receive(self, s):
        with self.lock:
            m = json.loads(s)
            print(bcolors.OKGREEN + 'Received from process: ' + json.dumps(m, indent=4) + bcolors.ENDC)

            if m['message'] == 'state-req':
                self.message = 'state-resp'
                stuff = self.send_data([m['id']], self.message_str())
            if m['message'] == 'state-resp':
                if self.transaction['state'] in ['committed', 'aborted']:
                    if self.transaction['number'] <= m['transaction']['number'] \
                            and isinstance(m['coordinator'], (int, int)):
                        self.coordinator = m['coordinator']
                        self.data = m['data']
                        self.transaction = m['transaction']
                else:
                    # TODO: recovery code here.
                    pass

            if m['message'] == 'vote-req':
                print(f'{bcolors.OKGREEN}Received vote-req{bcolors.ENDC}')
                self.c_t_vote_req.suspend()
                if 'crashBeforeVote' in self.flags and self.id != self.coordinator:
                    del self.flags['crashBeforeVote']
                    self.crash()

                self.transaction = m['transaction']
                # self.alive = m['alive']
                if 'vetonext' in self.flags:
                    self.message = 'vote-no'
                    del self.flags['vetonext']
                else:
                    print(f'{bcolors.OKGREEN}Voting yes{bcolors.ENDC}')
                    self.message = 'vote-yes'
                # self.log()
                self.send_data([m['id']], self.message_str())
                self.c_t_prec.restart()
                if 'crashAfterVote' in self.flags and self.id != self.coordinator:
                    del self.flags['crashAfterVote']
                    self.crash()

            if m['message'] == 'vote-yes' and self.id == self.coordinator:
                self.votes[m['id']] = True
                # Everybody has voted yes!
                if len(self.alive) == len(self.votes) and all(self.votes.values()):
                    self.p_t_vote.suspend()
                    self.message = 'precommit'
                    if 'crashPartialPreCommit' in self.flags:
                        # self.send_data(self.flags['crashPartialPreCommit'], self.message_str())
                        del self.flags['crashPartialPreCommit']
                        self.log()
                        self.crash()
                    else:
                        self.send_data(self.alive, self.message_str())
                        self.log()
                    self.p_t_acks.restart()

            if m['message'] == 'vote-no' and self.id == self.coordinator:
                self.p_t_vote.suspend()
                self.message = 'abort'
                self.votes[m['id']] = False
                self.log()
                self.send_data(self.alive, self.message_str())

            if m['message'] == 'precommit':
                self.c_t_prec.suspend()
                self.message = 'ack'
                self.transaction['state'] = 'precommitted'
                self.send_data([self.coordinator], self.message_str())
                self.log()
                self.c_t_commit.restart()
                if 'crashAfterAck' in self.flags:
                    del self.flags['crashAfterAck']
                    self.crash()

            if m['message'] == 'ack' and self.id == self.coordinator and self.transaction['state'] == 'precommitted':
                self.acks[m['id']] = True
                if len(self.acks) == len(self.alive):
                    self.p_t_acks.suspend()
                    self.message = 'commit'
                    self.log()
                    if 'crashPartialCommit' in self.flags:
                        # self.send_data(self.flags['crashPartialCommit'], self.message_str())
                        del self.flags['crashPartialCommit']
                        self.crash()
                    else:
                        self.send_data(self.alive, self.message_str())

            if m['message'] == 'commit' and self.transaction['state'] == 'precommitted':
                self.c_t_commit.suspend()
                m['transaction']['state'] = 'committed'

                if m['transaction']['action'] == 'add':
                    if m['transaction']['song'] not in self.data:
                        self.data[m['transaction']['song']] = m['transaction']['URL']
                        self.transaction_list.append(m['transaction'])

                elif m['transaction']['action'] == 'edit':
                    if m['transaction']['song'] in self.data:
                        self.data[m['transaction']['song']] = m['transaction']['URL']
                        self.transaction_list.append(m['transaction'])
                else:
                    del self.data[m['transaction']['song']]
                    self.transaction_list.append(m['transaction'])
                self.log()
                self.transaction['state'] = 'committed'
                self.c_t_vote_req.restart()
                if self.id == self.coordinator:
                    self.send_data([-1], 'ack commit')

            if m['message'] == 'abort' and self.transaction['state'] not in ['aborted', 'committed']:
                self.c_t_prec.suspend()
                m['transaction']['state'] = 'aborted'
                self.transaction_list.append(m['transaction'])
                self.log()
                self.transaction['state'] = 'aborted'
                self.c_t_vote_req.restart()
                if self.id == self.coordinator:
                    self.send_data([-1], 'ack abort')
            # reelection-protocol
            if m['message'] == 're-elect-coordinator':
                self.message = 'alive-list'
                self.send_data([m['id']], self.message_str())
                # Here we wait
            if m['message'] == 'alive-list':
                self.num_messages_received_for_election += 1
                l1 = self.alive
                l2 = m['alive'] # latest alive list
                print(f'{bcolors.OKGREEN}Latest alive list: {l2}{bcolors.ENDC}')
                self.alive = copy(l2) #[val for val in l1 if val in l2]
                if len(self.election_alive_list) == self.num_messages_received_for_election:
                    self.coordinator = min(self.alive)
                    print(f'{bcolors.OKGREEN}Decided new coordinator: {str(self.coordinator)}{bcolors.ENDC}')
                    print(f'{bcolors.OKGREEN}pid = {self.id}, coord = {self.coordinator}{bcolors.ENDC}')
                    if self.coordinator == self.id:
                        # tell master about new coordinator
                        print(f'{bcolors.OKGREEN}This process is the new coordinator: {str(self.id)}{bcolors.ENDC}')
                        self.send_data([-1], f'coordinator {self.id}')
                        if self.transaction['state'] == 'precommitted':
                            self.message = 'commit'
                            self.send_data(self.alive, self.message_str())
                        else:
                            self.message = 'abort'
                            self.send_data(self.alive, self.message_str())


                    self.c_t_vote_req.restart()
        print(f"{bcolors.OKGREEN}End receive{bcolors.ENDC}")
