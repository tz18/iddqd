"""Byte-level comparison within the LP2 batch (full images 17-74): the two solved pages (73 An End, 74 Parable)
against the 56 unsolved pages. Header segments (everything before the entropy-coded scan), scan tail, sizes,
and identity with the liber-primus__images--unsolved copies."""
import os, struct, hashlib, collections
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'liber-primus__images--full')
UNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'liber-primus__images--unsolved')
def segments(b):
    i = 2; segs = []
    while True:
        m = b[i + 1]
        if m == 0xD9: return segs, i
        L = struct.unpack('>H', b[i + 2:i + 4])[0]; seg = b[i:i + 2 + L]; segs.append((m, seg))
        j = i + 2 + L
        if m == 0xDA:
            scan_start = j
            while not (b[j] == 0xFF and b[j + 1] != 0 and not 0xD0 <= b[j + 1] <= 0xD7): j += 1
            segs.append(('scan', b[scan_start:j]))
        i = j
h = lambda x: hashlib.md5(x).hexdigest()[:8]
rows = {}
for n in range(17, 75):
    f = f'{n:02d}.jpg'; b = open(os.path.join(IMG, f), 'rb').read()
    segs, eoi = segments(b)
    hdr = {}
    for m, s in segs:
        if m == 'scan': continue
        hdr.setdefault(hex(m), []).append(h(s))
    scan = [s for m, s in segs if m == 'scan'][0]
    app0 = [s for m, s in segs if m == 0xE0][0]
    rows[f] = dict(kind='solved' if n >= 73 else 'unsolved', size=len(b), hdr={k: tuple(v) for k, v in hdr.items()},
                   order=tuple(hex(m) if m != 'scan' else 'scan' for m, s in segs), app0=app0[4:].hex(),
                   tail=scan[-8:].hex(), lastbyte=scan[-1], bpp=len(scan) * 8 / (2400 * 3600))
def summarize(key, fn=lambda r, k: r[k]):
    for kind in ('solved', 'unsolved'):
        c = collections.Counter(str(fn(r, key)) for r in rows.values() if r['kind'] == kind)
        print(f'   {kind:8s} {dict(c.most_common(4))}')
print('segment order:'); summarize('order')
print('APP0 (JFIF) bytes:'); summarize('app0')
for m, name in (('0xe2', 'APP2 (ICC profile)'), ('0xdb', 'DQT (quantization)'), ('0xc0', 'SOF0 (frame)'), ('0xc4', 'DHT (Huffman)'), ('0xda', 'SOS (scan header)')):
    print(name + ':'); summarize(m, lambda r, k: r['hdr'].get(k))
print('last byte of scan data (padding bits):'); summarize('lastbyte', lambda r, k: format(r[k], '08b'))
for kind in ('solved', 'unsolved'):
    rs = [r for r in rows.values() if r['kind'] == kind]
    print(f'{kind:8s} bits per pixel: min {min(r["bpp"] for r in rs):.3f} max {max(r["bpp"] for r in rs):.3f}')
# Huffman tables optimized per image? (count distinct DHT sets)
print('distinct Huffman table sets among unsolved:', len({r['hdr'].get('0xc4') for r in rows.values() if r['kind'] == 'unsolved'}))
# identity with the separate unsolved folder
full_h = {h(open(os.path.join(IMG, f'{n:02d}.jpg'), 'rb').read()): n for n in range(0, 75)}
same = sum(1 for f in os.listdir(UNS) if h(open(os.path.join(UNS, f), 'rb').read()) in full_h)
print(f'liber-primus__images--unsolved files byte-identical to a full image: {same} of {len(os.listdir(UNS))}')
# how the entropy-coded data ends: run of zero bytes before the end, per page
print('\ntrailing run of 0x00 bytes at the end of the scan data, and zero bytes in the last 2000 scan bytes:')
for kind in ('solved', 'unsolved'):
    vals = []
    for n in range(17, 75):
        f = f'{n:02d}.jpg'
        if rows[f]['kind'] != kind: continue
        b = open(os.path.join(IMG, f), 'rb').read(); segs, eoi = segments(b)
        scan = [s for m, s in segs if m == 'scan'][0]
        k = 0
        while k < len(scan) and scan[-1 - k] in (0x00,) or (k == 0 and scan[-1] != 0 and False): k += 1
        # allow the final padding byte to be non-zero
        body = scan[:-1] if scan[-1] != 0 else scan
        r = 0
        while r < len(body) and body[-1 - r] == 0: r += 1
        vals.append((f, r, body[-2000:].count(0)))
    print(f'   {kind:8s}', sorted(vals, key=lambda x: -x[1])[:6], '... median run', sorted(v[1] for v in vals)[len(vals)//2])
