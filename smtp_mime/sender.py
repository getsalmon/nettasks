import socket
import ssl

import sys

import b64
from credentials import Credentials
from letter import Letter


class Sender:
    def __init__(self, args, server_address):
        self.server, self.port = server_address.server, server_address.port
        self.rcpt = args.rcpt
        self.path = args.path
        self.credentials = Credentials(args)
        self.security = args.security.lower()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(args.timeout)

        if self.security == "ssl":
            try:
                self.socket = ssl.wrap_socket(self.socket)
                self.connect()
            except (ssl.SSLError, socket.timeout):
                self.crush("Couldn't start SSL connection")
            self.ehlo()
        elif self.security == "empty":
            self.connect()
            self.ehlo()
        elif self.security == "tls":
            self.connect()
            self.start_tls()
        if not self.credentials.is_empty():
            self.auth()
        self.letter = Letter(args, self.credentials.login)
        self.send()

    def send(self):
        print(self.letter.mail_from)
        self.socket.send(self.letter.mail_from)
        ans = self.get_ans()
        if ans[:3] != '250':
            self.crush("Error when send mail from")
        print(self.letter.rcpt_to)

        self.socket.send(self.letter.rcpt_to)
        ans = self.get_ans()
        if ans[:3] != '250':
            self.crush("Error when send rcpt to")
        print("data")
        self.socket.send(b"data\r\n")
        ans = self.get_ans()
        if ans[:3] != '334' and ans[:3] != "354":
            self.crush("Error when send data request")

        self.socket.send(self.letter.content.encode(encoding="utf-8"))
        self.socket.send(b"\r\n.\r\n")
        ans = self.get_ans()
        if ans[0:3] == "250":
            print("\nLetter was send\n")
        else:
            self.crush("Letter wasn't send")
        self.socket.send(b"quit\r\n")
        self.socket.close()

    def auth(self):
        print("auth login")
        self.socket.send(b"auth login\r\n")
        _ = self.get_ans()
        login = bytes(b64.encode(self.credentials.login) + '\r\n',
                      encoding="utf8")
        print(login)
        self.socket.send(login)
        _ = self.get_ans()
        password = bytes(b64.encode(self.credentials.password) + '\r\n',
                         encoding="utf8")
        print(password)
        self.socket.send(password)
        ans = self.get_ans()
        if ans[:3] != "235":
            self.crush("Auth wasn't successful")

    def connect(self):
        try:
            self.socket.connect((self.server, self.port))
            ans = self.get_ans()
            if ans[:3] != "220":
                raise ValueError()
        except (socket.timeout, ValueError, ConnectionRefusedError) as e:
            self.crush("Connection wasn't established")

    def start_tls(self):
        try:
            print("STARTTLS")
            self.socket.send(b"STARTTLS\r\n")
            ans = self.get_ans()
            if ans[:3] != '220':
                self.crush("Couldn't start TLS connection")
            else:
                self.socket = ssl.wrap_socket(self.socket,
                                              ssl_version=ssl.PROTOCOL_TLSv1)
        except:
            self.crush("Couldn't start TLS connection")
        self.ehlo()

    def ehlo(self):
        print("EHLO Antoshka")
        self.socket.send(b"EHLO Antoshka\r\n")
        ans = self.get_ans()
        if ans[:3] != "250":
            self.crush("We can't say EHLO to server")

    def crush(self, msg):
        try:
            print("quit")
            self.socket.send(b"quit\r\n")
            self.socket.close()
        except:
            pass
        print(msg)
        sys.exit()

    def get_ans(self):
        byties = b''
        while True:
            try:
                temp = self.socket.recv(1024)
                if temp != b'':
                    byties += temp
                else:
                    break
            except socket.timeout:
                break
        ans = byties.decode("UTF-8")
        sys.stderr.write(ans)
        return ans
