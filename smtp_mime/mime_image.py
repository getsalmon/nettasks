import b64
import textwrap

class MimeImage:
    def __init__(self, path):
        self.path = path
        self.name = path.split("/")[-1]
        self.ext = self.name.split(".")[-1]
        self.byties = self.encode_image()
        self.content = self.create_content()

    def encode_image(self):
        f = open(self.path, "rb").read()
        return b64.encode(f)

    def create_content(self):
        return 'Content-Type: image/{ext}\r\n' \
               'Content-Disposition: attachment; filename="{name}"\r\n' \
               'Content-Transfer-Encoding: base64\r\n\r\n' \
               '{data}'.format(ext=self.ext,
                               name=self.to_utf8(self.name),
                               data=self.wrap(self.byties))

    @staticmethod
    def to_utf8(s):
        return "=?utf-8?b?{}?=".format(b64.encode(s.encode(encoding='utf-8')))

    @staticmethod
    def wrap(s):
        return "\n".join(textwrap.wrap(s, 120))