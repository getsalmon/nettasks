import json
import socket
import select
import argparse
import re
import threading
import sre_constants
import sys

LOCALHOST = "127.0.0.1"
HEADER400 = (
    b"HTTP/1.1 400 Bad Request\r\n"
    b"Connection: Close\r\n\r\n"
)


class Query:
    def __init__(self, byties):
        self.byties = byties
        self.text = byties.decode('utf-8')
        self.is_connect = self.text.split('\n')[0].split(' ')[0] == "CONNECT"
        self.host = self.get_host()
        self.path = self.get_path()
        self.address = self.build_address()

    def get_host(self):
        splitted = self.text.split('\n')
        ans = ""
        for x in splitted:
            if x.startswith("Host: "):
                ans = x.split(" ")[1]
                break
        return ans.strip()

    def get_path(self):
        return self.text.split('\n')[0].split(' ')[1]

    def build_address(self):
        if self.path.startswith("http"):
            return self.path
        else:
            return self.host + self.path


class Server:
    def __init__(self, args):
        port = args.port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', port))
        self.conn = args.connections
        self.verbose = args.verbose
        self.socket.listen(self.conn)
        self.blacklist = []
        self.timeout = args.timeout

        self.pool = []
        if args.blacklist:
            self.blacklist = self._get_black_list(args.blacklist)

    @staticmethod
    def _get_black_list(bl):
        f = json.load(open(bl, encoding='utf-8'))
        ans = []
        for x in f:
            try:
                ans.append(re.compile(x))
            except sre_constants.error:
                print("Blacklist regex %s is not valid" % x)
        return ans

    def action(self, query, conn):
        q = Query(query)
        ans = b""
        if self.is_in_blacklist(q.address):
            if self.verbose:
                print(q.address + " is blacklisted")
            conn.send(HEADER400)
            return
        if q.is_connect:
            return
        if self.verbose:
            print(q.address)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        try:
            s.connect((q.host, 80))
        except:
            print("fail with " + q.host)
            return
        s.send(q.byties)
        ans = self.get_ans(s)
        conn.send(ans)

    def is_in_blacklist(self, address):
        for x in self.blacklist:
            if re.match(x, address):
                return True
        return False

    def get_ans(self, sock):
        byties = b''
        while True:
            try:
                temp = sock.recv(65535)
                if temp != b'':
                    byties += temp
                else:
                    break
            except socket.timeout:
                break
        return byties

    def main_loop(self):
        print("Server was launched.")
        while True:
            try:
                ready = select.select((self.socket,), (), (), self.timeout)
                if ready[0]:
                    conn, addr = self.socket.accept()
                    query = conn.recv(8192)  # default http request size, as I see
                    if query == b"":
                        continue
                    while True:
                        if threading.active_count() <= self.conn:
                            conn.settimeout(self.timeout)
                            t = threading.Thread(target=self.action,
                                                 args=(query, conn))
                            t.daemon = True
                            t.start()
                            self.pool.append(t)
                            break
            except KeyboardInterrupt:
                print("Killed")

                sys.exit()
            except socket.error as e:
                print(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=8080,
                        help="Port to connect")
    parser.add_argument("--connections", "-c", type=int, default=100,
                        help="Amount of connections")
    parser.add_argument('-t', '--timeout', type=float, default=1)
    parser.add_argument('-b', '--blacklist', type=str, default=None)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    Server(args).main_loop()


if __name__ == "__main__":
    main()
