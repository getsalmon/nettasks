B64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcde" \
               "fghijklmnopqrstuvwxyz0123456789+/"


def decode(text):
    raw_bits = ""
    for letter in text:
        if letter != "=":
            a = B64_ALPHABET.index(letter)
            raw_bits += str(bin(a)[2:]).zfill(6)
        else:
            raw_bits += "000000"
    result = b""
    i = 0
    while i < len(raw_bits):
        result += int(raw_bits[i: i + 8], 2).to_bytes(1, "little")
        i += 8
    return result
