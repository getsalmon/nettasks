import verifier
import letter
import sender
import argparse
import server_address


def main():
    p = argparse.ArgumentParser()
    p.add_argument("rcpt", type=str, help="Recipient email address")
    p.add_argument("server", type=str, help="Required SMTP server "
                                            "[format ip:port]")
    p.add_argument("--path", "-p", type=str, help="Pics path", default=".")
    p.add_argument("--security", "--sec", "-s",
                   choices=['tls', 'ssl', 'TLS', 'SSL', "empty"],
                   default="empty")
    p.add_argument("--login", "-l", type=str, help="Your mail login",
                   default=None)
    p.add_argument("--credentials", "-c", type=str,
                   help="Path to json file with your mail credentials",
                   default=None)
    p.add_argument("--timeout", "-t", type=float,
                   help="Connection timeout",
                   default=2)
    p.add_argument("--pattern", type=str,
                   help="Path to json letter pattern",
                   default="letter.json")
    args = p.parse_args()

    verifier.Verifier(args)
    sender.Sender(args, server_address.ServerAddress(args))


if __name__ == '__main__':
    main()
