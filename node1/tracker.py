import json
from sys import argv
# import libraries
from socket import *
from threading import Lock, Thread


class Tracker:
    # need to know my listening address
    def __init__(self, tracker_addr):
        # peer list (p2p port for each node)
        self.peer_list = []
        self.peer_lock = Lock()

        # broadcast list
        self.conns = []
        self.broadcast_lock = Lock()

        # listening socket
        self.listen_sock = socket(AF_INET, SOCK_STREAM)
        self.listen_sock.bind(tracker_addr)
        print("**Running at : ", tracker_addr, "**")

        # set candidates list
        self.candi_list = [
            {"candidate_name": "Mike", "number": 1},
            {"candidate_name": "Jenny", "number": 2},
            {"candidate_name": "Tom", "number": 3},
        ]


    # handle new connections
    def start_listening(self):
        self.listen_sock.listen()
        print("**Start listening**")

        while True:
            # get new connection
            conn, addr = self.listen_sock.accept()
            print("**New connection accepted**")

            # add that socket to conns
            self.broadcast_lock.acquire()
            self.conns.append(conn)
            self.broadcast_lock.release()

            # kick off new thread to handle that connection
            handle_thread = Thread(target=self.handle_conn, args=(conn,))
            handle_thread.start()
    
    # thread to handle a connection
    def handle_conn(self, conn):
        while True:
            # receive message
            msg = json.loads(conn.recv(1500).decode())
            # new connection

            if msg['type'] == 'SYN':
                print("**Connected with Node", msg['addr'], "**")
                # add to peer list
                self.peer_lock.acquire()
                self.peer_list.append(msg['addr'])
                self.peer_lock.release()

                # broadcast peer update
                self.broadcast_peer_list()

                # broadcast candidates list
                self.broadcast_candi_list()

            # stop connection
            elif msg['type'] == 'FIN':
                print("**Disconnected with Node", msg['addr'], "**")
                # remove peer from peer list 
                self.peer_lock.acquire()
                self.peer_list.remove(msg['addr'])
                self.peer_lock.release()

                # remove connecton from broadcast list
                self.broadcast_lock.acquire()
                self.conns.remove(conn)
                self.broadcast_lock.release()

                # broadcast update
                self.broadcast_peer_list()
                break

        # clean up
        conn.shutdown(SHUT_RDWR)
        conn.close()
        
    
    def broadcast_peer_list(self):
        # codify peer list
        self.peer_lock.acquire()
        peer_list = json.dumps(self.peer_list).encode()
        self.peer_lock.release()

        # broadcast it
        self.broadcast_lock.acquire()
        for conn in self.conns:
            conn.send(peer_list)
        self.broadcast_lock.release()

    def broadcast_candi_list(self):
        candi_list = json.dumps(self.candi_list).encode()
        for conn in self.conns:
            conn.send(candi_list)


if __name__ == "__main__":
    host = gethostname()
    port = int(argv[1])
    Tracker(tracker_addr=(host, port)).start_listening()