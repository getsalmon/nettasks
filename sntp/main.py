import socket
import argparse
import threading
import struct
import time

START = 2208988800
FORMAT = "!BBBBII4sQQQQ"


class Server:
    def __init__(self, argv):
        self._sec = argv.sec
        port = argv.port
        self._verb = argv.verbose
        self._connections = argv.connections
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                   socket.getprotobyname('UDP'))
        self._sock.bind(('127.0.0.1', port))
        self._pool = []

    def loop(self):
        while True:
            query, addr = self._sock.recvfrom(1024)
            while True:
                if threading.active_count() <= self._connections:
                    t = threading.Thread(target=self._main,
                                         args=(query, addr))
                    t.start()
                    self._pool.append(t)
                    break

    def _get_time(self):
        return self._get_long_num(time.time() + START + self._sec)

    def _get_long_num(self, num):
        return int(num * 2 ** 32)

    def pack_packet(self, start_time, time):

        ans = struct.Struct(FORMAT).pack(0b00100100,
                                         3, 0, 0, 0, 0,
                                         b'Fake', self._get_time(),
                                         start_time, time,
                                         self._get_time())
        return ans

    def _main(self, query, addr):
        start_time = struct.unpack(FORMAT, query)[10]
        recv_time = self._get_time()
        if self._verb:
            print("I lied again ({} seconds, address: {})".format(self._sec, addr[0]))
        self._sock.sendto(self.pack_packet(start_time, recv_time), addr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    parser.add_argument("sec", type=int, help="amount of mistake in seconds")
    parser.add_argument('-t', '--timeout', dest='timeout', action='store',
                        type=float, default=0.3,
                        help='Timeout in seconds, default 0.3 seconds')
    parser.add_argument("-p", "--port", type=int, help="port to connect", default=5000) # port 123 is denied on mac osx
    parser.add_argument('-c', '--connections', type=int, dest='connections',
                        action='store', default=10,
                        help='Number of connections, ten is default')
    args = parser.parse_args()
    Server(args).loop()
