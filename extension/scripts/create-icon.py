"""Deterministic vector-style PNG icon; standard library only."""
from pathlib import Path
import struct
import zlib

SIZE = 256
SCALE = 2
BACKGROUND = (16, 43, 66)
CYAN = (90, 226, 221)
WHITE = (229, 244, 251)
DARK = (8, 27, 44)


def rounded(x, y, left, top, right, bottom, radius):
    if not left <= x <= right or not top <= y <= bottom:
        return False
    cx = max(left + radius, min(right - radius, x))
    cy = max(top + radius, min(bottom - radius, y))
    return (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2


def line(x, y, x1, y1, x2, y2, width):
    dx, dy = x2-x1, y2-y1
    t = max(0, min(1, ((x-x1)*dx + (y-y1)*dy) / (dx*dx+dy*dy)))
    return (x-x1-t*dx)**2 + (y-y1-t*dy)**2 <= (width/2)**2


def pixel(x, y):
    if not rounded(x, y, 2, 2, 254, 254, 42):
        return (0, 0, 0, 0)
    color = BACKGROUND
    if rounded(x, y, 46, 28, 210, 229, 20):
        color = CYAN
    if rounded(x, y, 55, 37, 201, 220, 13):
        color = DARK
    if rounded(x, y, 72, 53, 141, 61, 4):
        color = WHITE
    if rounded(x, y, 72, 177, 184, 185, 4):
        color = WHITE
    if rounded(x, y, 72, 194, 146, 201, 3):
        color = (93, 128, 155)
    for coords in [(102, 86, 78, 110), (78, 110, 102, 134), (153, 86, 177, 110), (177, 110, 153, 134), (138, 79, 118, 141)]:
        if line(x, y, *coords, 9):
            color = CYAN
    return (*color, 255)


def chunk(name, data):
    return struct.pack('!I', len(data)) + name + data + struct.pack('!I', zlib.crc32(name + data) & 0xffffffff)


rows = []
for y in range(SIZE):
    row = bytearray([0])
    for x in range(SIZE):
        samples = [pixel(x+(sx+0.5)/SCALE, y+(sy+0.5)/SCALE) for sy in range(SCALE) for sx in range(SCALE)]
        row.extend(round(sum(p[channel] for p in samples)/len(samples)) for channel in range(4))
    rows.append(bytes(row))
png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', SIZE, SIZE, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b''.join(rows), 9)) + chunk(b'IEND', b'')
(Path(__file__).resolve().parents[1] / 'resources/icon.png').write_bytes(png)
