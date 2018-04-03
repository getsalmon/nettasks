import json
import os
import re
import sys


class Verifier:
    def __init__(self, args):
        self._security = args.security

        self._check_email(args.rcpt, "rcpt")
        self._check_pattern_file(args.pattern)
        if args.credentials:
            self._check_credentials_file(args.credentials)
        if args.login:
            self._check_email(args.login, "login")

    @staticmethod
    def _check_email(email, scope):
        pattern = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\."
                             "[a-zA-Z0-9-.]+$)")
        if not pattern.match(email):
            print("Error in %s address" % scope)
            sys.exit()

    @staticmethod
    def _check_credentials_file(path):
        if not os.path.isfile(path):
            print("Credentials file not found")
            sys.exit()
        f = open(path, encoding='utf8')
        cred = json.load(f)
        if "login" not in cred or "password" not in cred:
            print("Error in credentials file")
            sys.exit()

    @staticmethod
    def _check_pattern_file(path):
        if not os.path.isfile(path):
            print("Pattern file not found")
            sys.exit()
        f = open(path, encoding='utf8')
        cred = json.load(f)
        if not {"sender_email"}.issubset(cred.keys()):
            print("Error in pattern file")
            sys.exit()
