import json
import getpass


class Credentials:
    def __init__(self, args):
        self.login = ""
        self.password = ""
        if args.credentials:
            f = open(args.credentials, encoding='utf8')
            cred = json.load(f)
            self.login = cred["login"]
            self.password = cred["password"]
        elif args.login:
            self.login = args.login
            self.password = getpass.getpass()

    def is_empty(self):
        return self.login == "" and self.password == ""
