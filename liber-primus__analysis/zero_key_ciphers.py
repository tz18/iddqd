"""Modern ciphers with an all-zero key (and zero IV/nonce).
(a) As keystream generators: keystream bytes -> rune values (mod 29 / mod 28 + 1 / reject >= 232 / 5-bit chunks),
    subtracted from or added to the runes, raw or autokey-removed, keystream restarting for the whole text,
    each segment or each page. Score: IoC (random 1.00, English ~1.73, English + book key ~1.05).
(b) As block/stream decryption of the runes encoded as bytes (index bytes, GP-value bytes, Latin ASCII, base-29
    packing, 5-bit packing). Score: share of output bytes that are rune indices (< 29) or printable ASCII."""
import os, json, warnings
import numpy as np
warnings.filterwarnings('ignore')
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
try:
    from cryptography.hazmat.decrepit.ciphers import algorithms as old
except Exception:
    old = algorithms
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
PRV = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
LAT = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
rows = [(IDX[t[1]], l['s'], p['page']) for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
c = np.array([r[0] for r in rows]); seg = np.array([r[1] for r in rows]); page = np.array([r[2] for r in rows])
dstream = np.concatenate([[0], (c[1:] - c[:-1]) % 29])
def restart(groups):
    idx = np.zeros(len(groups), int)
    for i in range(1, len(groups)): idx[i] = 0 if groups[i] != groups[i - 1] else idx[i - 1] + 1
    return idx
positions = {'whole text': np.arange(len(c)), 'each segment': restart(seg), 'each page': restart(page)}
def ioc(x):
    cnt = np.bincount(x % 29, minlength=29); n = len(x); return (cnt * (cnt - 1)).sum() / (n * (n - 1)) * 29
NB = 80000
def mk(alg, mode=None):
    return Cipher(alg, mode) if mode is not None else Cipher(alg, None)
generators = {}
def add(name, fn):
    try: generators[name] = fn()
    except Exception as e: print('skip', name, type(e).__name__, e)
zero = lambda n: bytes(n)
for bits in (128, 192, 256):
    add(f'AES-{bits} CTR', lambda b=bits: mk(algorithms.AES(zero(b // 8)), modes.CTR(zero(16))).encryptor().update(zero(NB)))
    add(f'AES-{bits} OFB', lambda b=bits: mk(algorithms.AES(zero(b // 8)), modes.OFB(zero(16))).encryptor().update(zero(NB)))
    add(f'AES-{bits} ECB(zeros)', lambda b=bits: mk(algorithms.AES(zero(b // 8)), modes.ECB()).encryptor().update(zero(NB)))
add('ChaCha20', lambda: mk(algorithms.ChaCha20(zero(32), zero(16))).encryptor().update(zero(NB)))
add('Camellia-128 CTR', lambda: mk(algorithms.Camellia(zero(16)), modes.CTR(zero(16))).encryptor().update(zero(NB)))
add('SM4 CTR', lambda: mk(algorithms.SM4(zero(16)), modes.CTR(zero(16))).encryptor().update(zero(NB)))
for kl in (5, 16, 32):
    add(f'RC4 key {kl} zero bytes', lambda k=kl: mk(old.ARC4(zero(k))).encryptor().update(zero(NB)))
for nm, alg, kl, bl in (('3DES', 'TripleDES', 24, 8), ('Blowfish', 'Blowfish', 16, 8), ('CAST5', 'CAST5', 16, 8), ('IDEA', 'IDEA', 16, 8), ('SEED', 'SEED', 16, 16)):
    A = getattr(old, alg, None)
    if A is None: continue
    add(f'{nm} OFB', lambda A=A, kl=kl, bl=bl: mk(A(zero(kl)), modes.OFB(zero(bl))).encryptor().update(zero(NB)))
    add(f'{nm} CTR', lambda A=A, kl=kl, bl=bl: mk(A(zero(kl)), modes.CTR(zero(bl))).encryptor().update(zero(NB)))
print('keystream generators:', len(generators))
def reductions(ks):
    b = np.frombuffer(ks, np.uint8).astype(int)
    out = {'mod 29': b % 29, 'mod 28 + 1': b % 28 + 1, 'reject >= 232': (b[b < 232] % 29)}
    bits = np.unpackbits(np.frombuffer(ks, np.uint8)); n5 = len(bits) // 5
    out['5-bit mod 29'] = (bits[:n5 * 5].reshape(-1, 5) @ (1 << np.arange(4, -1, -1))) % 29
    return out
res = []
for gname, ks in generators.items():
    for rname, K in reductions(ks).items():
        for pname, pos in positions.items():
            k = K[pos]
            for tname, tgt in (('raw', c), ('autokey removed', dstream)):
                for op in ('-', '+'):
                    v = ioc(tgt - k if op == '-' else tgt + k)
                    res.append((v, gname, rname, pname, tname, op))
res.sort(reverse=True)
print('(a) keystream: %d combinations. Highest IoC:' % len(res))
for r in res[:6]: print('    %.4f  %s | %s | restart %s | %s | %s' % r)
print('    baseline: autokey-removed text alone scores %.4f (missing doublets); raw text %.4f' % (ioc(dstream), ioc(c)))
ks0 = np.frombuffer(generators['IDEA OFB'][:64], np.uint8) if 'IDEA OFB' in generators else None
print('    IDEA zero-key OFB keystream, first bytes:', ks0[:24].tolist() if ks0 is not None else None)
# (b) decryption of the runes as bytes
def enc_variants():
    v = {'rune index bytes': bytes(c.tolist()), 'GP value bytes': bytes(PRV[x] for x in c),
         'Latin ASCII': ''.join(LAT[x] for x in c).encode()}
    bits = ''.join(format(x, '05b') for x in c); v['5-bit packed'] = int(bits[:len(bits) // 8 * 8], 2).to_bytes(len(bits) // 8, 'big')
    big = 0
    for x in c[:3000]: big = big * 29 + int(x)
    v['base-29 packed (first 3000 runes)'] = big.to_bytes((big.bit_length() + 7) // 8, 'big')
    return v
def score(out):
    b = np.frombuffer(out, np.uint8)
    return (b < 29).mean(), ((b >= 32) & (b < 127) | (b == 10)).mean()
dec = []
for ename, data in enc_variants().items():
    for nm, make in (('AES-128', lambda: algorithms.AES(zero(16))), ('AES-256', lambda: algorithms.AES(zero(32))),
                     ('Camellia-128', lambda: algorithms.Camellia(zero(16))), ('SM4', lambda: algorithms.SM4(zero(16))),
                     ('3DES', lambda: old.TripleDES(zero(24))), ('Blowfish', lambda: old.Blowfish(zero(16))),
                     ('CAST5', lambda: old.CAST5(zero(16))), ('IDEA', lambda: old.IDEA(zero(16)))):
        try: A = make()
        except Exception: continue
        bl = A.block_size // 8
        for mname, M in (('ECB', modes.ECB()), ('CBC', modes.CBC(zero(bl))), ('CFB', modes.CFB(zero(bl))), ('OFB', modes.OFB(zero(bl))), ('CTR', modes.CTR(zero(bl)))):
            dd = data[:len(data) // bl * bl] if mname in ('ECB', 'CBC') else data
            try: out = Cipher(A, M).decryptor().update(dd)
            except Exception: continue
            dec.append((*score(out), ename, nm, mname))
    for nm, make in (('ChaCha20', lambda: Cipher(algorithms.ChaCha20(zero(32), zero(16)), None)), ('RC4-16', lambda: Cipher(old.ARC4(zero(16)), None))):
        out = make().decryptor().update(data); dec.append((*score(out), ename, nm, 'stream'))
print('\n(b) block/stream decryption: %d combinations (random: 11%% of bytes < 29, 37%% printable)' % len(dec))
for s in sorted(dec, reverse=True)[:4]: print('    rune-range %.1f%%  printable %.1f%%  %s | %s %s' % (100 * s[0], 100 * s[1], *s[2:]))
for s in sorted(dec, key=lambda x: -x[1])[:4]: print('    printable %.1f%%  rune-range %.1f%%  %s | %s %s' % (100 * s[1], 100 * s[0], *s[2:]))
