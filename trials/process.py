import json
import threading


class Client:
    def __init__(self, pid, num_procs, send, c_t_vote_req):
        # Array of processes that we think are alive.
        self.alive = [pid]
        # True if a process restarts
        self.stupid = False
        # Unknown coordinator.
        self.coordinator = None
        # Internal hash table of URL : song_name.
        self.data = {}
        # Flags to crash at a certain moment, or to vote no.
        self.flags = {}
        # Process id.
        self.id = pid
        # Single global lock.
        self.lock = threading.Lock()
        self.logfile = '%dlog.p' % pid
        # Message to send. Possible values are:
        # abort, ack, commit, just-woke, state-resp, state-req, ur-elected,
        # vote-no, vote-req, vote-yes
        self.message = 'state-req'
        # Total number of processes (not including master).
        self.num_processes = num_procs
        # Send functionL
        self.send = send
        # All known information about current transaction.
        self.transaction = {'number': 0,
                            'song' : None,
                            'state' : 'committed',
                            'action': None,
                            'URL' : None}
        self.num_messages_received_for_election = 0

        # Timeouts
        self.c_t_vote_req = c_t_vote_req
        # self.c_t_prec = c_t_prec
        # self.c_t_c = c_t_c
        # self.p_t_vote = p_t_vote
        # self.p_t_acks = p_t_acks
        # Alive list for re-election protocol
        self.election_alive_list = [pid]
        # Wait for a vote-req
        self.c_t_vote_req.restart()

    def simple_dict(self):
        return {'alive' : self.alive,
                   'coordinator' : self.coordinator,
                   'data' : self.data,
                   'flags' : self.flags,
                   'id' : self.id,
                   'message' : self.message,
                   'transaction' : self.transaction}

    def message_str(self):
        to_send = self.simple_dict()
        result = json.dumps(to_send)
        return result

    def load_state(self):
        print(f'Process {self.id} alive for the first time')
        # Find out who is alive and who is the coordinator.
        self.alive = self.broadcast()
        # Self is the first process to be started.
        if len(self.alive) == 1:
            self.coordinator = self.id
            # Tell master this process is now coordinator.
            self.send([0], 'coordinator %d' % self.id)

    def broadcast(self):
        recipients = range(1, self.num_processes+1) # PID of all processes.
        message = self.message_str() # Serialize self.
        return self.send(recipients, message)