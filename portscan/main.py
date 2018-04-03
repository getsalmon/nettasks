import socket
import argparse
import sys
import json
import os
import ports_db
import threading


class Portscan:
    def __init__(self, args):
        self._start, self._end = Portscan._parse_range(args.ports)
        self._address = Portscan._get_address(args.addr)
        self._known_ports = Portscan._get_known_ports()
        self._pool = []

    @staticmethod
    def _get_address(ip):
        try:
            return socket.gethostbyname(ip)
        except socket.gaierror:
            print('Hostname could not be resolved. Check spelling or Internet connection.')
            sys.exit()

    @staticmethod
    def _get_known_ports():
        if os.path.exists('tcp_ports.json'):
            with open('tcp_ports.json') as a:
                return json.loads(a.read())
        else:
            return ports_db.create_db()

    @staticmethod
    def _parse_range(port_range):
        numbers = [int(x) for x in port_range.split('-')]
        if len(numbers) == 2:
            return numbers[0], numbers[1] + 1
        if len(numbers) == 1:
            return numbers[0], numbers[0] + 1

    def _is_tcp_port_open(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(args.timeout)
            result = sock.connect_ex((self._address, port))
            sock.close()
            return result == 0
        except socket.error as e:
            print("Couldn't connect to server")
            sys.exit()

    def _get_name(self, port, proto):
        name = "undef"
        str_port = str(port)
        if str_port in self._known_ports:
            return " | ".join(self._known_ports[str_port])
        return name

    def _print_result(self, port):
        res = self._is_tcp_port_open(port)
        if res:
            name = self._get_name(port, 'tcp')
            print('Port [{}/{}] ({}) is opened'.format(
                port, 'tcp', name
            ))
        if not res and args.verbose:
            print('Port [{}/{}] is closed'.format(
                port, 'tcp'
            ))

    def scan(self):
        for port in range(self._start, self._end):
            while True:
                if threading.activeCount() <= args.connections:
                    t = threading.Thread(target=self._print_result, args=(port,))
                    t.start()
                    self._pool.append(t)
                    break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    parser.add_argument("addr", type=str, help="address which TCP ports is needed to be scanned")
    parser.add_argument("ports", type=str, help="one port or many ports to be scanned", default="1-1024")
    parser.add_argument('-t', '--timeout', dest='timeout', action='store', type=float, default=0.3,
                        help='Timeout in seconds, default 0.3 seconds')
    parser.add_argument('-c', '--connections', type=int, dest='connections', action='store',
                        default=10, help='Number of connections, ten is default')
    args = parser.parse_args()

    Portscan(args).scan()
