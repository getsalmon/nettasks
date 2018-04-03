import argparse
import socket
import ssl
import getpass
import server_address
import sys
import letter

CRLF = b"\r\n"


class POP3:
    def __init__(self, args, addr):
        self.login = args.login
        self.addr, self.port = addr.server, addr.port
        self.passw = getpass.getpass()
        self.security = args.security.lower()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(args.timeout)

        self.determine_security_and_connect()
        try:
            self.print_letters(args.range_let)
        except KeyboardInterrupt:
            self.crush("Cancelled")

    def determine_security_and_connect(self):
        if self.security == "ssl":
            try:
                self.socket = ssl.wrap_socket(self.socket)
                self.connect()
            except (ssl.SSLError, socket.timeout):
                self.crush("Couldn't start SSL connection")
        elif self.security == "empty":
            self.connect()
        elif self.security == "tls":
            self.connect()
            self.start_tls()
        self.auth()

    def print_letters(self, range_let):
        if range_let != "":
            start, end = self.parse_range(range_let)
        else:
            start, end = 1, self.get_amount()
        for i in range(start, end + 1):
            self.retr(i)
            i += 1

    def parse_range(self, r):
        try:
            g = r.split("-")
            if len(g) == 1:
                return int(g[0]), int(g[0])
            if len(g) == 2:
                return int(g[0]), int(g[1])
        except ValueError:
            self.crush("error while parsing range")

    def connect(self):
        try:
            self.socket.connect((self.addr, self.port))
            ans = self.get_ans()
            if not self.is_ok(ans):
                raise ValueError()
        except (socket.timeout, ValueError, ConnectionRefusedError) as e:
            self.crush("Connection wasn't established")

    def start_tls(self):
        self.socket.send(b"STLS" + CRLF)
        r = self.get_ans()
        if self.is_ok(r):
            self.socket = ssl.wrap_socket(self.socket,
                                          ssl_version=ssl.PROTOCOL_TLSv1)
        else:
            self.crush("Couldn't start TLS")

    def auth(self):
        self.socket.send(b"USER " + self.login.encode('utf-8') + CRLF)
        r = self.get_ans()
        if not self.is_ok(r):
            self.crush("Couldn't send user cmd")
        self.socket.send(b"PASS " + self.passw.encode('utf-8') + CRLF)
        r = self.get_ans()
        if not self.is_ok(r):
            self.crush("Couldn't send pass cmd")

    def crush(self, msg):
        try:
            self.socket.send(b"quit\r\n")
            self.socket.close()
        except:
            pass
        print(msg)
        sys.exit()

    def retr(self, n):
        self.socket.send(b"RETR " + str(n).encode("utf-8") + CRLF)
        r = self.get_ans()
        if (len(r)) > 0:
            letter.Letter(r).print_letter()

    def get_amount(self):
        self.socket.send(b"STAT" + CRLF)
        r = self.get_ans()
        if self.is_ok(r):
            return int(r.decode('utf-8').split(' ')[1])

    def get_ans(self):
        byties = b''
        while True:
            try:
                temp = self.socket.recv(65535)
                if temp != b'':
                    byties += temp
                else:
                    break
            except socket.timeout:
                break

        return byties

    @staticmethod
    def is_ok(response):
        return response[:3] == b"+OK"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("addr", type=str, help="server address [addr:port]")

    p.add_argument("login", type=str, help="your login")
    p.add_argument("-r", "--range_let", type=str,
                   help="letters range", default="")
    p.add_argument("--security", "--sec", "-s", type=str,
                   choices=['tls', 'ssl', 'TLS', 'SSL', "empty"],
                   default="empty")
    p.add_argument("--timeout", "-t", type=float,
                   help="Connection timeout",
                   default=0.5)
    args = p.parse_args()
    addr = server_address.ServerAddress(args)
    POP3(args, addr)


if __name__ == '__main__':
    main()
