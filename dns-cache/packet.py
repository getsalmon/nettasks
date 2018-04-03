import struct

HEADER_LENGTH = 12
HEADER_FORMAT = "!HHHHHH"
CLASSES = {
    1: 'IN',
    2: 'CS',
    3: 'CH',
    4: 'HS'
}
TYPES = {
    1: 'A',
    2: 'NS',
    3: 'MD',
    4: 'MF',
    5: 'CNAME',
    6: 'SOA',
    7: 'MB',
    8: 'MG',
    9: 'MR',
    10: 'NULL',
    11: 'WKS',
    12: 'PTR',
    13: 'HINFO',
    14: 'MINFO',
    15: 'MX',
    16: 'TXT',
    28: 'AAAA',
    99: 'SPF',
    255: 'ANY'
}


class DNSPacketParser:
    def __init__(self, data):
        self.data = data
        self.header = self.parse_header()
        self.id = self.header[0]
        self.qr = self.parse_packet_type()
        self.qd_count = self.header[2]
        self.an_count = self.header[3]
        self.ns_count = self.header[4]
        self.ar_count = self.header[5]
        self.pointer = HEADER_LENGTH
        self.questions = self.parse_questions()
        self.answers = self.parse_answers()

    def parse_header(self):
        return struct.unpack(HEADER_FORMAT, self.data[:12])


    def parse_packet_type(self):
        flags = self.header[1]
        qr = flags >> 15
        return qr

    def parse_questions(self):
        questions = []
        for i in range(self.qd_count):
            q = Question(self.data, self.pointer)
            questions.append(q)
            self.pointer += q.full_length
        return questions

    def parse_answers(self):
        ans = []
        for i in range(self.an_count):
            a = Answer(self.data, self.pointer)
            ans.append(a)
            self.pointer += a.full_length
        return ans


class Record:
    def __init__(self, data, start):
        self.data = data
        self.start = start
        self.name_length, self.name = self.get_name(self.start)
        self.type = self.get_type()
        self.class_ = self.get_class()

    def get_name(self, pointer):
        true_length = 0
        true_name = b""
        remote_started = False
        while True:
            start_byte = struct.unpack("!H",
                                       self.data[pointer: pointer + 2])[0]
            need_to_jump = not remote_started and start_byte >> 14 == 3
            remote_started = remote_started or need_to_jump
            pointer = start_byte & 0x3fff if need_to_jump else pointer
            name, length = self._read_name_part(pointer)
            true_name += name
            pointer += length
            if not remote_started:
                true_length += length
            if self.data[pointer] == 0:
                true_name += b'\x00'
                if remote_started:
                    true_length += 2  # pointer length
                else:
                    true_length += 1  # zero byte
                break
        return true_length, true_name

    def _read_name_part(self, start):
        length = self.data[start]
        return self.data[start: start + length + 1], length + 1

    def get_type(self):
        begin = self.start + self.name_length
        end = begin + 2
        type = struct.unpack('!H', self.data[begin:end])[0]
        return TYPES[type]

    def get_class(self):
        begin = self.start + self.name_length + 2
        end = begin + 2
        class_ = struct.unpack("!H", self.data[begin:end])[0]
        return CLASSES[class_]


class Question(Record):
    def __init__(self, data, start):
        super().__init__(data, start)
        self.full_length = self.name_length + 4
        self.bytes = self.data[self.start: self.start + self.full_length]
        del self.data


class Answer(Record):
    def __init__(self, data, start):
        super().__init__(data, start)
        self.ttl = self.get_ttl()
        self.rd_length = self.get_rdata_len()
        self.rd_data = self.get_rdata()
        self.rd_data = self.parse_rdata()
        self.full_length = self.name_length + 10 + self.rd_length
        start = self.start + self.name_length
        end = self.start + self.name_length + 10
        self.bytes = self.name + self.data[start: end] + self.rd_data
        del self.data

    def get_ttl(self):
        begin = self.start + self.name_length + 4
        end = begin + 4
        return struct.unpack('!I', self.data[begin:end])[0]

    def get_rdata_len(self):
        begin = self.start + self.name_length + 8
        end = begin + 2
        return struct.unpack('!H', self.data[begin:end])[0]

    def get_rdata(self):
        begin = self.start + self.name_length + 10
        end = begin + self.rd_length
        return self.data[begin: end]

    def parse_rdata(self):
        if self.type == "NS":
            pointer = self.start + self.name_length + 10
            val = self.get_name(pointer)[1]
            return val
        else:
            return self.rd_data


def build_response(pack, answers, ns):
    id = pack.header[0]
    flags = 0x8180
    qd_count = pack.qd_count
    an_count = len(answers)
    ns_count = pack.ns_count
    ar_count = 0
    header = struct.pack(HEADER_FORMAT, id, flags,
                         qd_count, an_count, ns_count, ar_count)
    val = header
    questions = pack.questions
    for q in questions:
        val += q.bytes
    for a in answers:
        val += a.ans.bytes
    for n in ns:
        val += n.bytes
    return val
