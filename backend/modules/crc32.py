import struct

def crc32(data, crc):
    for d in data:
        crc = (crc ^ d) & 0xFFFFFFFF
        for i in range(32):
            if crc & 0x80000000:
                crc = ((crc << 1) & 0xFFFFFFFF) ^ 0x04C11DB7
            else:
                crc = (crc << 1) & 0xFFFFFFFF
        crc = crc & 0xFFFFFFFF
    return crc


def crc32_bytes(data):
    crc = 0xFFFFFFFF
    d32 = []

    llen = len(data) % 4

    if llen > 0:
        for i in range(4 - llen):
            data = data + b"\xff"

    wlen = int(len(data) / 4)

    fmstr = "<"
    for i in range(wlen):
        fmstr = fmstr + "I"
    d32 = d32 + list(struct.unpack(fmstr, data[0:wlen * 4]))

    return crc32(d32, crc)