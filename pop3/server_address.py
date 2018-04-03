import sys


class ServerAddress:
    def __init__(self, args):
        parts = args.addr.split(":")
        self.sec = args.security
        self.server = ""
        self.port = ""
        if len(parts) == 1:
            self.server = parts[0]
            self.port = self.ask_port()
        elif len(parts) == 2:
            self.server = parts[0]
            if self.check_port(parts[1]):
                self.port = int(parts[1])
            else:
                self.port = self.ask_port()
        else:
            print("Error in server")
            sys.exit(0)

    def check_port(self, port):
        try:
            int(port)
            return True
        except ValueError:
            return False

    def _std_port(self):
        return {"TLS": 110, "tls": 110, "ssl": 995,
                "SSL": 995, "empty": 110}[self.sec]

    def ask_port(self):
        while True:
            port = input("Write port or press "
                         "enter to use standard [{}]: ".format(
                self._std_port()))
            if port == "":
                port = self._std_port()
            if self.check_port(port):
                return int(port)
