import socket
import threading
import packet
import time
from cache import CacheRecord
import sys
IP = "127.0.0.1"

cache = dict()


class Server:
    def __init__(self, argv):
        self.forw_port = argv.forw_port
        self.forw_ip = argv.forw_ip
        self.port = argv.port
        self.retries = argv.retries
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((IP, self.port))
        self.pool = []
        self.is_updated = False
        self.check_if_me()
        self.main_loop()

    def check_if_me(self):
        try:
            forwarder_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            forwarder_s.settimeout(0.2)
            forwarder_s.sendto(b"hello", (self.forw_ip, self.forw_port))
            recv = forwarder_s.recv(4096)
            if recv == b"hello":
                self.sock.close()
                forwarder_s.close()
                print("It's my clone!")
                sys.exit()
        except socket.error:
            pass
        
    def main_loop(self):
        while True:
            data, addr = self.sock.recvfrom(4096)
            t = threading.Thread(target=self.work,
                                 args=(data, addr))
            t.start()
            self.pool.append(t)

    def work(self, data, addr):
        if data == b"hello":
            self.sock.sendto(b"hello", addr)
            return
        p = packet.DNSPacketParser(data)
        for question in p.questions:
            type_ = question.type
            name = question.name
            # there is no [type] answers or CNAME
            if type_ != "ANY" and name not in cache or \
                    (type_ not in cache[name] and "CNAME" not in cache[name]):
                self.ask_forw(data)
                if self.is_updated:
                    self.is_updated = False
                else:
                    resp = packet.build_response(p, [], [])
                    self.sock.sendto(resp, addr)
                    continue
            ans = self.get_answer(question, data)
            if not self.validate_ttl(ans):
                self.update_all_answers_for_question(question, data)
                print("TTL!")
                ans = self.get_answer(question, data)
            resp = packet.build_response(p, ans, [])
            self.sock.sendto(resp, addr)

    def get_answer(self, question, data):
        type_ = question.type
        name = question.name
        # if any - get all answers from server
        if type_ == "ANY":
            ans = self.update_all_answers_for_question(question, data)
        # if cname is available - give it
        elif type_ not in cache[name] and "CNAME" in cache[name]:
            ans = cache[question.name]["CNAME"]
        # normal answer
        else:
            ans = cache[question.name][question.type]
        print("Taking from cache")
        return ans

    def update_all_answers_for_question(self, question, data):
        cache[question.name] = {}
        self.ask_forw(data)
        ans = []
        for x in cache[question.name]:
            ans += cache[question.name][x]
        return ans

    def validate_ttl(self, ans):
        for a in ans:
            if time.time() - a.time > a.ttl:
                return False
        return True

    def ask_forw(self, data):
        print("Asking")
        forwarder_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        forwarder_s.settimeout(0.1)
        for i in range(self.retries):
            try:
                forwarder_s.sendto(data, (self.forw_ip, self.forw_port))
                response = forwarder_s.recv(4096)
                response_packet = packet.DNSPacketParser(response)
                for q in response_packet.answers:
                    if q.name not in cache:
                        cache[q.name] = {}
                    if q.type not in cache[q.name]:
                        cache[q.name][q.type] = []
                    cache[q.name][q.type].append(CacheRecord(q))
                    self.is_updated = True
                break
            except socket.error:
                print("Waiting...")
                continue
