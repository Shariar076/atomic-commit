import json
import os
import threading

from res.globals import bcolors


class Client:
    def __init__(self, pid, num_procs, send, p_t_vote, p_t_acks):
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
        self.send = send
        self.transaction = {'number': 0,
                            'song': None,
                            'state': 'committed',
                            'action': None,
                            'URL': None}
        self.transaction_list = []
        self.num_messages_received_for_election = 0
        self.p_t_vote = p_t_vote
        self.p_t_acks = p_t_acks
        self.election_alive_list = [pid]

    def simple_dict(self):
        return {'alive': self.alive,
                'coordinator': self.coordinator,
                'data': self.data,
                'flags': self.flags,
                'id': self.id,
                'message': self.message,
                'transaction': self.transaction}

    def load_state(self):
        print(f'{bcolors.OKGREEN}Process {self.id} alive for the first time{bcolors.ENDC}')
        self.alive = self.broadcast()
        if len(self.alive) == 1:
            self.coordinator = self.id
            self.send([-1], f'coordinator {self.id}')

    def re_election_protocol(self):
        with self.lock:
            print(f'{bcolors.OKGREEN}Starting re-election{bcolors.ENDC}')
            self.num_messages_received_for_election = 0
            self.message = 'lets-elect-coordinator'
            self.election_alive_list = self.broadcast()

            for p in self.alive:
                if p not in self.election_alive_list:
                    self.alive.remove(p)

    def after_timed_out_on_acks(self):
        with self.lock:
            self.message = 'commit'
            self.send(self.alive, self.message_str())
            self.log()

    def broadcast(self):
        recipients = range(self.N)  # PID of all processes.
        message = self.message_str()  # Serialize self.
        return self.send(recipients, message)

    def log(self):
        pass

    def message_str(self):
        to_send = self.simple_dict()
        result = json.dumps(to_send)
        return result

    def print_playlist(self):
        print(f'{bcolors.OKGREEN}Current playlist of pid {self.id}: {self.data}{bcolors.ENDC}')

    def print_transactions(self):
        print(f'{bcolors.OKGREEN}Current transactions by pid {self.id}: {self.transaction_list}{bcolors.ENDC}')

    def receive_master(self, s):
        print(f'{bcolors.OKGREEN}Received from master: {str(s)}{bcolors.ENDC}')
        with self.lock:
            parts = s.split()
            if parts[0] in ['add', 'edit', 'delete']:
                if self.coordinator == self.id:
                    self.transaction = {'number': self.transaction['number'] + 1,
                                        'song': parts[1],
                                        'state': 'uncertain',
                                        'action': parts[0],
                                        'URL': parts[2] if parts[0] in ['add', 'edit'] else None}
                    self.message = 'vote-req'
                    self.acks = {}
                    self.votes = {}
                    if 'crashVoteREQ' in self.flags:
                        self.send(self.flags['crashVoteREQ'], self.message_str())
                        del self.flags['crashVoteREQ']
                        self.log()
                        os._exit(1)
                    else:
                        self.alive = self.broadcast()
                        print(f'{bcolors.OKGREEN}Self alive = {self.alive}{bcolors.ENDC}')
                        self.log()
                        self.p_t_vote.restart()
                else:
                    self.send([-1], 'ack abort')
            elif parts[0] == 'crash':
                os._exit(1)

            elif parts[0] == 'get':
                if parts[1] in self.data:
                    url = self.data[parts[1]]
                    self.send([-1], 'resp ' + url)
                else:
                    self.send([-1], 'resp NONE')
            # elif parts[0] == 'vote' and parts[1] == 'NO':
            #     self.flags['vote NO'] = True
        print(f'{bcolors.OKGREEN}End receive_master{bcolors.ENDC}')

    def receive(self, s):
        print(f'{bcolors.OKGREEN}{bcolors.BOLD}Received from process {s}{bcolors.ENDC}')
        with self.lock:
            m = json.loads(s)

            if m['message'] == 'abort' and self.transaction['state'] not in ['aborted', 'committed']:
                self.transaction['state'] = 'abort'
                self.log()

            if m['message'] == 'ack' and self.id == self.coordinator and self.transaction['state'] == 'precommitted':
                self.acks[m['id']] = True
                if len(self.acks) == len(self.alive):
                    self.p_t_acks.suspend()
                    self.message = 'commit'
                    self.log()
                    if 'crashPartialCommit' in self.flags:
                        self.send(self.flags['crashPartialCommit'], self.message_str())
                        del self.flags['crashPartialCommit']
                        os._exit(1)
                    else:
                        self.send(self.alive, self.message_str())
                    self.send([-1], 'ack commit')

            if m['message'] == 'commit' and self.transaction['state'] == 'precommitted':
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

            if m['message'] == 'precommit':
                self.message = 'ack'
                self.transaction['state'] = 'precommitted'
                self.send([self.coordinator], self.message_str())
                self.log()
                if 'crashAfterAck' in self.flags:
                    del self.flags['crashAfterAck']
                    os._exit(1)

            if m['message'] == 'state-req':
                self.message = 'state-resp'
                stuff = self.send([m['id']], self.message_str())
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
                self.transaction = m['transaction']
                # self.alive = m['alive']
                if 'vetonext' in self.flags:
                    self.message = 'vote-no'
                    self.transaction['state'] = 'aborted'
                    del self.flags['vetonext']
                else:
                    print(f'{bcolors.OKGREEN}Voting yes{bcolors.ENDC}')
                    self.message = 'vote-yes'
                self.log()
                self.send([m['id']], self.message_str())
                if 'crashAfterVote' in self.flags and self.id != self.coordinator:
                    del self.flags['crashAfterVote']
                    os._exit(1)

            if m['message'] == 'vote-no' and self.id == self.coordinator:
                self.p_t_vote.suspend()
                self.message = 'abort'
                self.transaction['state'] = 'aborted'
                self.votes[m['id']] = False
                self.log()
                self.send(self.alive, self.message_str())
                self.send([-1], 'ack abort')

            if m['message'] == 'vote-yes' and self.id == self.coordinator:
                self.votes[m['id']] = True
                # Everybody has voted yes!
                if len(self.alive) == len(self.votes) and all(self.votes.values()):
                    self.p_t_vote.suspend()
                    self.message = 'precommit'
                    self.transaction['state'] = 'precommitted'
                    if 'crashPartialPreCommit' in self.flags:
                        self.send(self.flags['crashPartialPreCommit'], self.message_str())
                        del self.flags['crashPartialPreCommit']
                        self.log()
                        os._exit(1)
                    else:
                        self.send(self.alive, self.message_str())
                        self.log()
                    self.p_t_acks.restart()

        print(f"{bcolors.OKGREEN}End receive{bcolors.ENDC}")
