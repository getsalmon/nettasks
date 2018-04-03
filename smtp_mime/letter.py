import json
import os
import random
import string
import textwrap
import b64
from credentials import Credentials
from mime_image import MimeImage


class Letter:
    def __init__(self, args, login):
        self.rcpt_to = ("rcpt to: <%s>\r\n" % args.rcpt).encode()
        self.login = login
        self.path = args.path
        self.pattern = json.load(open(args.pattern, encoding="utf-8"))
        self.sender = self.get_sender()
        self.recipient = args.rcpt
        self.mail_from = ("mail from: <%s>\r\n" % self.sender).encode()
        self.images = [MimeImage(x) for x in self.get_images_paths()]
        self.body = self.pattern["body"].replace('\n', '\r\n')
        self.boundary = self.create_safe_boundary()
        self.content = self.build_letter()

    def get_sender(self):
        if self.login:
            return self.login
        else:
            return self.pattern["sender_email"]

    def build_letter(self):
        sender_name = self.to_utf8(self.pattern["sender_name"])
        recipient_name = self.to_utf8(self.pattern["recipient_name"])
        subj = self.to_utf8(self.pattern["subject"])
        template = "From: {sender_name} <{sender_email}> \r\n" \
                   "To: {recipient_name} <{recipient_email}>\r\n" \
                   "Subject: {subject}\r\n" \
                   "Content-Type: multipart/mixed; boundary={boundary}\r\n" \
                   "\r\n" \
                   "--{boundary}\r\n" \
                   "Content-Type: text/html; charset=utf-8\r\n" \
                   "\r\n" \
                   "{body}\r\n" \
                   "\r\n".format(sender_name=sender_name,
                                 sender_email=self.sender,
                                 recipient_name=recipient_name,
                                 recipient_email=self.recipient,
                                 subject=subj,
                                 body=self.body,
                                 boundary=self.boundary)

        for x in self.images:
            template += '--{boundary}\r\n{content}\r\n'.format(
                content=x.content,
                boundary=self.boundary)
        template += "--{}--".format(self.boundary)
        return template

    @staticmethod
    def to_utf8(s):
        return "=?utf-8?b?{}?=".format(b64.encode(s.encode(encoding='utf-8')))

    @staticmethod
    def create_boundary(n):
        return ''.join(random.choice(string.ascii_lowercase + string.digits +
                                     string.ascii_uppercase) for _ in range(n))

    def create_safe_boundary(self):
        while True:
            stop = False
            boundary = self.create_boundary(32)
            if boundary in self.body:
                continue
            for x in self.images:
                if boundary in x.content:
                    stop = True
                    break
            if stop:
                continue
            break
        return boundary

    def get_images_paths(self):
        for (dir_path, dir_names, file_names) in os.walk(self.path):
            for f in file_names:
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', 'bmp')):
                    yield (dir_path + "/" + f)
