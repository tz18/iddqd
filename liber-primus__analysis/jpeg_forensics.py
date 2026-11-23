"""Compare JPEG files of solved vs unsolved pages (encoder settings, metadata, appended data),
and decode the data appended to 05.jpg."""
import os, json, hashlib, collections, struct, re, binascii
from PIL import Image, JpegImagePlugin
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, '..', 'liber-primus__images--full')
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
kind = {p['img']: ('unsolved' if {l['s'] for l in p['lines']} & set(range(7, 16)) else 'solved') for p in d['pages']}
def end_of_image(b):
    """walk JPEG markers; return offset just after the EOI that ends the image"""
    i = 2
    while i < len(b):
        m = b[i + 1]
        if m == 0xD9: return i + 2
        L = struct.unpack('>H', b[i + 2:i + 4])[0]; j = i + 2 + L
        if m == 0xDA:
            while not (b[j] == 0xFF and b[j + 1] != 0 and not 0xD0 <= b[j + 1] <= 0xD7): j += 1
        i = j
rows = []
for f in sorted(os.listdir(IMG)):
    b = open(os.path.join(IMG, f), 'rb').read(); im = Image.open(os.path.join(IMG, f))
    q = hashlib.md5(json.dumps({k: list(v) for k, v in im.quantization.items()}).encode()).hexdigest()[:8]
    rows.append((f, kind.get(f, 'no runes'), im.mode, q, 'icc_profile' in im.info, len(b) - end_of_image(b)))
for g in ('solved', 'unsolved', 'no runes'):
    rs = [r for r in rows if r[1] == g]
    print(f'{g:9s} {len(rs):2d} images | mode {dict(collections.Counter(r[2] for r in rs))} | quant tables {dict(collections.Counter(r[3] for r in rs))} '
          f'| ICC {sum(r[4] for r in rs)} | with appended data {[(r[0], r[5]) for r in rs if r[5]]}')
# 05.jpg: image + "\n\n" + reversed hex of the magic square text + the image bytes reversed
b = open(os.path.join(IMG, '05.jpg'), 'rb').read(); e = end_of_image(b); tail = b[e:]
m = re.match(rb'([\n\r]*)([0-9a-fA-F]+)', tail); hx = m.group(2); rest = tail[len(m.group(1)) + len(hx):]
print('\n05.jpg appended text (hex, reversed):'); print(binascii.unhexlify(hx[::-1][: len(hx) // 2 * 2]).decode())
print('05.jpg appended binary equals the image bytes reversed:', rest == b[:e][::-1])
# 10.jpg: its appended data is exactly 11.jpg + 12.jpg + 13.jpg concatenated
b = open(os.path.join(IMG, '10.jpg'), 'rb').read(); parts = [open(os.path.join(IMG, f), 'rb').read() for f in ('11.jpg', '12.jpg', '13.jpg')]
e = len(b) - sum(map(len, parts))
print('10.jpg appended data == 11.jpg + 12.jpg + 13.jpg:', b[e:] == b''.join(parts) and end_of_image(b) == e)
