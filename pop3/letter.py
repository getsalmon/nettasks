import re
import b64
import quopri


class Letter:
    def __init__(self, byties):
        self.lines = byties.split(b'\r\n')
        self.from_ = ""
        self.to = ""
        self.date = ""
        self.subj = "Subject: <empty>"
        try:
            self.size = "Size: " + self.lines[0].split(b' ')[1].decode('utf-8') \
                        + " bytes"
        except IndexError:
            self.size = ""
        for i in range(len(self.lines)):
            if self.lines[i].startswith(b"From: "):
                self.from_ = self.lines[i] + self.continue_reading(i + 1)
            elif self.lines[i].startswith(b"To: "):
                self.to = self.lines[i] + self.continue_reading(i + 1)
            elif self.lines[i].startswith(b"Subject: "):
                self.subj = self.lines[i] + self.continue_reading(i + 1)
            elif self.lines[i].startswith(b"Date: "):
                self.date = self.lines[i] + self.continue_reading(i + 1)

    def continue_reading(self, i):
        res = b""
        while True:
            if self.lines[i].startswith(b"\t") or self.lines[i].startswith(
                    b" "):
                res += self.lines[i].strip(b" ").strip(b"\t")
                i += 1
            else:
                return res
        return res

    def print_letter(self):
        print(self.decode(self.to))
        print(self.decode(self.from_))
        print(self.decode(self.subj))
        print(self.decode(self.date))
        print(self.size)
        print("+=================================+")

    def decode(self, byties):
        if not isinstance(byties, bytes):
            return byties
        pattern = re.compile(
            "=\?(?P<enc>.*?)\?(?P<qb>[BbQq])\?(?P<text>.*?)\?=")
        try:
            string = byties.decode('utf-8')
        except UnicodeError:
            return str(byties)[2:-1]
        found = re.finditer(pattern, string)
        for part in found:
            try:
                enc, qb, text = part.group("enc"), part.group("qb").lower(), \
                                part.group("text")
                if qb == "q":
                    new_part = quopri.decodestring(text).decode(enc,
                                                                errors="ignore")
                elif qb == "b":
                    new_part = b64.decode(text).decode(enc, errors="ignore")
                string = string.replace(part.group(), new_part)
            except:
                return str(byties)[2:-1]
        return string
