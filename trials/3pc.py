from server import Server
from client import Client
import sys, getopt
from threading import Thread
from time import sleep


def get_host_port(argv):
    host = None
    port = None
    try:
        opts, args = getopt.getopt(argv, "h:p:", ["host=", "port="])
    except getopt.GetoptError:
        print('test.py -h <host> -p <port>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--host"):
            host = str(arg)
        elif opt in ("-p", "--port"):
            port = int(arg)
    print(f"host: {host}")
    print(f"port: {port}")
    return host, port


if __name__ == "__main__":
    host, port = get_host_port(sys.argv[1:])
    server = Server(host, port)
    server_thread = Thread(target=server.start_server)
    server_thread.start()
    client = Client()
    client.connect_server(host, port)
    sleep(1)
    print(server.clients)




