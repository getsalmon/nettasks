import server
import argparse

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("forw_ip", type=str,
                   help="Forwarder IP")
    p.add_argument("forw_port", type=int,
                   help="Forwarder Port")
    p.add_argument("-r", '--retries', type=int,
                   help="Amount of retries while connecting to forwarder",
                   default=5)
    p.add_argument("-p", "--port", type=int,
                   help="Your server port", default=53)
    argv = p.parse_args()
    server.Server(argv)
