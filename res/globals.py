client = None
root_port = 20000
address = 'localhost'
processes = dict()
threads = dict()
conns = dict()
outgoing_conns = dict()
my_pid = -2

timeout_wait = 5
timeout_vote_req = 60

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == '__main__':
    print(f"{bcolors.HEADER}HEADER{bcolors.ENDC}")
    print(f"{bcolors.WARNING}HEADER{bcolors.ENDC}")
    print(f"{bcolors.FAIL}HEADER{bcolors.ENDC}")
    print(f"{bcolors.BOLD}HEADER{bcolors.ENDC}")
    print(f"{bcolors.UNDERLINE}HEADER{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}HEADER{bcolors.ENDC}")
    print(f"{bcolors.OKCYAN}HEADER{bcolors.ENDC}")
    print(f"{bcolors.OKGREEN}HEADER{bcolors.ENDC}")