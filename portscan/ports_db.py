import urllib.request
import json
import re

MY_PORTS_TXT = "http://avefablo.xyz/ports.txt"  # faster (copy located in Pervouralsk)
PORTS_TXT = "https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.txt"


def create_db():
    raw = {}
    req = urllib.request.urlopen(MY_PORTS_TXT)
    while True:
        line = req.readline().decode('utf-8')
        if line == '':
            break
        if re.match('^(\w|-)+( +\d+)( +(tcp))', line):
            splitted_line = [x.strip() for x in re.split(' +', line)][:3]
            name = splitted_line[0]
            port = splitted_line[1]
            if port in raw:
                raw[port].append(name)
            else:
                raw[port] = [name]
    req.close()
    return raw


if __name__ == '__main__':
    db = create_db()
    file = open('tcp_ports.json', 'w')
    json.dump(db, file, sort_keys=True)
    file.close()
