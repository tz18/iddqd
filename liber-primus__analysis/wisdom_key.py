"""Use the 3,368-byte 'wisdom' / 'folly' file from the 2013 CicadaOS disc (/tmp/wisdom, identical to /tmp/folly)
as a key on the unsolved runes. Conversions: byte mod 29, byte mod 28 + 1, reject >= 232, 5-bit chunks, base-29
digits of the whole file (big- and little-endian). Applied cyclically at every offset (and restarting each
segment), added or subtracted, to the raw text, the autokey-removed stream, and the mod-28 non-zero stream.
Also hash-derived AES-256 / AES-128 / ChaCha20 keystreams. Score: IoC (random 1.00; a correct key covering even
a quarter of the text gives > 1.15)."""
import os, json, hashlib, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
W = open(os.path.join(HERE, '..', '2013', '02', 'wisdom'), 'rb').read()
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
rows = [(IDX[t[1]], l['s'], p['page']) for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
c = np.array([r[0] for r in rows]); seg = np.array([r[1] for r in rows]); page = np.array([r[2] for r in rows])
dstream = (c[1:] - c[:-1]) % 29
nz = dstream[dstream != 0] - 1                      # mod-28 values of the non-zero steps
def restart(groups):
    idx = np.zeros(len(groups), int)
    for i in range(1, len(groups)): idx[i] = 0 if groups[i] != groups[i - 1] else idx[i - 1] + 1
    return idx
seg_pos = restart(seg)
b = np.frombuffer(W, np.uint8).astype(int)
bits = np.unpackbits(np.frombuffer(W, np.uint8))
def base29(bs, order):
    n = int.from_bytes(bs, order); out = []
    while n: n, r = divmod(n, 29); out.append(r)
    return np.array(out[::-1])
keys = {'byte mod 29': b % 29, 'byte mod 28 + 1': b % 28 + 1, 'reject >= 232': b[b < 232] % 29,
        '5-bit chunks': (bits[:len(bits) // 5 * 5].reshape(-1, 5) @ (1 << np.arange(4, -1, -1))) % 29,
        'base-29 big-endian': base29(W, 'big'), 'base-29 little-endian': base29(W, 'little')}
def ioc(x, m=29):
    cnt = np.bincount(x, minlength=m); n = len(x); return (cnt * (cnt - 1)).sum() / (n * (n - 1)) * m
targets = {'raw': (c, 29), 'autokey removed': (dstream, 29), 'mod-28 non-zero steps': (nz, 28)}
res = []
for kname, K in keys.items():
    L = len(K)
    for tname, (T, m) in targets.items():
        n = len(T)
        for op in (1, -1):
            for o in range(L):
                k = K[(np.arange(n) + o) % L] % m
                res.append((ioc((T - op * k) % m, m), kname, tname, 'cyclic', op, o))
            if tname == 'raw':
                for o in range(0, L, 7):
                    k = K[(seg_pos + o) % L] % m
                    res.append((ioc((T - op * k) % m, m), kname, tname, 'restart each segment (step 7)', op, o))
# hash-derived modern keystreams
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
streams = {'AES-256-CTR(sha256)': Cipher(algorithms.AES(hashlib.sha256(W).digest()), modes.CTR(bytes(16))).encryptor().update(bytes(40000)),
           'AES-128-CTR(md5)': Cipher(algorithms.AES(hashlib.md5(W).digest()), modes.CTR(bytes(16))).encryptor().update(bytes(40000)),
           'ChaCha20(sha512[:32])': Cipher(algorithms.ChaCha20(hashlib.sha512(W).digest()[:32], bytes(16)), None).encryptor().update(bytes(40000))}
for sname, ks in streams.items():
    kb = np.frombuffer(ks, np.uint8).astype(int)
    for red, K in (('mod 29', kb % 29), ('mod 28 + 1', kb % 28 + 1), ('reject >= 232', kb[kb < 232] % 29)):
        for tname, (T, m) in targets.items():
            for op in (1, -1):
                res.append((ioc((T - op * (K[:len(T)] % m)) % m, m), sname + ' ' + red, tname, 'whole text', op, 0))
res.sort(key=lambda r: -r[0])
print('tests:', len(res))
for r in res[:8]: print('   IoC %.4f  key %s | %s | %s | sign %+d | offset %d' % r)
base = {t: ioc(T, m) for t, (T, m) in targets.items()}
print('baselines without any key:', {k: round(v, 4) for k, v in base.items()})
