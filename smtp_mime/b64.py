B64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcde" \
               "fghijklmnopqrstuvwxyz0123456789+/"


def encode(text):
    res = ''
    octets = ''
    if text in ['', b'']:
        return ''
    if isinstance(text, str):
        octets = ''.join(str.zfill(format(ord(x), 'b'), 8) for x in text)
    elif isinstance(text,  bytes):
        octets = ''.join(str.zfill(format(int(x), 'b'), 8) for x in text)
    to_enc = list(chunks(octets, 6))
    for i in to_enc:
        enc = int(str.ljust(i, 6, '0'), 2)
        res += B64_ALPHABET[enc]
    last = to_enc[-1]
    if len(last) == 2:
        res += '=='
    if len(last) == 4:
        res += '='
    return res


def chunks(st, n):
    for i in range(0, len(st), n):
        yield st[i:i+n]
