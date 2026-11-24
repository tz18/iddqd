"""Run candidate keystreams through the FULL model we arrived at:
    plaintext --rotate (rare letter -> 0)--> x --inner layer keyed by K, 0 kept fixed--> s --ciphertext autokey--> c
Undo: s[i] = c[i] - c[i-1] (mod 29). s == 0 -> the rare letter (doublet). For s != 0, undo the inner layer:
    'add28'  : x = 1 + ((s-1) - k) mod 28           (shift over the 28 non-zero symbols)
    'sub28'  : x = 1 + ((s-1) + k) mod 28   (key was subtracted when enciphering; k - s would only relabel add28)
    'mul29'  : x = s * k^-1 mod 29, k in 1..28      (multiplication keeps 0 fixed)
    'imul29' : x = s * k mod 29
Key advance: on every rune, or only on non-zero s (skip rule, like the solved pages' F).
The rotation is a shift, which does not change IoC, so it is not enumerated.
Score: IoC of x over the non-zero positions (28 symbols; random 1.00, English ~1.7).
A self-test encrypts English with a known random keystream and checks the harness recovers it."""
import os, sys, json, hashlib, warnings
import numpy as np
warnings.filterwarnings('ignore')
sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
rows = [(IDX[t[1]], l['s'], p['page']) for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
C = np.array([r[0] for r in rows]); SEG = np.array([r[1] for r in rows]); PAGE = np.array([r[2] for r in rows])
INV29 = np.array([0] + [pow(x, -1, 29) for x in range(1, 29)])
def ioc28(x):
    cnt = np.bincount(x, minlength=29)[1:]; n = cnt.sum(); return (cnt * (cnt - 1)).sum() / (n * (n - 1)) * 28
def undo(c, groups, K, op, skip, offset, per_group_restart):
    """c: ciphertext runes; groups: restart labels (autokey also restarts? no: autokey runs through, key may restart)"""
    s = (c[1:] - c[:-1]) % 29; g = groups[1:]
    nz = s != 0
    # key index per position
    step = nz.astype(int) if skip else np.ones(len(s), int)
    idx = np.cumsum(step) - step                       # index of the key value used at this position
    if per_group_restart:
        starts = np.r_[0, np.nonzero(g[1:] != g[:-1])[0] + 1]
        base = np.zeros(len(s), int)
        for a, b in zip(starts, list(starts[1:]) + [len(s)]): base[a:b] = idx[a]
        idx = idx - base
    k = K[(idx + offset) % len(K)]
    x = np.zeros(len(s), int)
    sv = s[nz]; kv = k[nz]
    if op == 'add28': x[nz] = 1 + ((sv - 1) - kv) % 28
    elif op == 'sub28': x[nz] = 1 + ((sv - 1) + kv) % 28
    elif op == 'mul29': x[nz] = sv * INV29[kv % 28 + 1] % 29
    else: x[nz] = sv * (kv % 28 + 1) % 29
    return ioc28(x[nz])
def scan(K, offsets=range(1), restarts=('none',)):
    best = (0, None)
    for op in ('add28', 'sub28', 'mul29', 'imul29'):
        for skip in (False, True):
            for rs in restarts:
                groups = {'none': np.zeros(len(C), int), 'segment': SEG, 'page': PAGE}[rs]
                for o in offsets:
                    v = undo(C, groups, K, op, skip, o, rs != 'none')
                    if v > best[0]: best = (v, (op, 'skip zeros' if skip else 'every rune', 'restart ' + rs, 'offset %d' % o))
    return best
# ---------------- self-test ----------------
exec(open(os.path.join(HERE, 'progressive_key.py')).read().split('dp = [')[0])   # P: English runes
Pn = np.array(P); rng = np.random.default_rng(5)
x = (Pn + 1) % 29                                   # rotate: EA (28) -> 0
Ktrue = rng.integers(0, 28, 20000)
c = [0]; j = 0
for xi in x:
    if xi == 0: s = 0
    else: s = 1 + ((xi - 1) + Ktrue[j]) % 28; j += 1      # add28, key skips zeros
    c.append((c[-1] + s) % 29)
cs = np.array(c[1:]); sim_groups = np.zeros(len(cs), int)
cs0 = np.r_[0, cs]; g0 = np.zeros(len(cs0), int)   # include the autokey's starting state so the first step is kept
right = undo(cs0, g0, Ktrue, 'add28', True, 0, False); wrongkey = undo(cs0, g0, rng.integers(0, 28, 20000), 'add28', True, 0, False)
shifted = max(undo(cs, sim_groups, Ktrue, 'add28', True, o, False) for o in range(5))
print(f'self-test on English: correct keystream IoC {right:.3f} (best over offsets 0-4 without the start state: {shifted:.3f}), wrong keystream {wrongkey:.3f}, doublet rate {(cs[1:]==cs[:-1]).mean():.2%}')
# ---------------- candidate keystreams ----------------
cands = {}
primes = []; n = 2
while len(primes) < 20000:
    if all(n % q for q in primes if q * q <= n): primes.append(n)
    n += 1
primes = np.array(primes)
cands['primes'] = primes; cands['totient(primes)'] = primes - 1
f = [1, 1]
while len(f) < 20000: f.append((f[-1] + f[-2]) % 812)
cands['fibonacci'] = np.array(f)
def pi_int(n):
    def at(x, u):
        s = t = u // x; x2 = x * x; k = 3; sg = -1
        while t: t //= x2; s += sg * (t // k); sg = -sg; k += 2
        return s
    u = 10 ** (n + 10); return 4 * (4 * at(5, u) - at(239, u)), u
PI, U = pi_int(21000)
cands['pi digits'] = np.array([int(ch) for ch in str(PI // 10 ** 10)][:20000])
cands['2pi digits'] = np.array([int(ch) for ch in str(2 * PI // 10 ** 10)][:20000])
W = open(os.path.join(HERE, '..', '2013', '02', 'wisdom'), 'rb').read()
cands['wisdom bytes'] = np.frombuffer(W, np.uint8).astype(int)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
def aes_stream(key32): return np.frombuffer(Cipher(algorithms.AES(key32), modes.CTR(bytes(16))).encryptor().update(bytes(20000)), np.uint8).astype(int)
cands['AES-256 zero key'] = aes_stream(bytes(32))
cands['ChaCha20 zero key'] = np.frombuffer(Cipher(algorithms.ChaCha20(bytes(32), bytes(16)), None).encryptor().update(bytes(20000)), np.uint8).astype(int)
cands['AES(sha256(wisdom))'] = aes_stream(hashlib.sha256(W).digest())
for word in ('circumference', 'CIRCUMFERENCE', 'divinity', 'DIVINITY', 'firfumferenfe', 'instar', 'INSTAR', 'emerge', '3301', '1033', '761',
             'parable', 'liber primus', 'LIBER PRIMUS', 'the key is all around you', '1231507051321', 'the primes are sacred', 'totient', 'cicada'):
    cands[f'AES(sha256("{word}"))'] = aes_stream(hashlib.sha256(word.encode()).digest())
print('\ncandidate keystreams through the full model (best over 4 inner ops x 2 key-advance rules x offsets):')
results = []
for name, K in cands.items():
    offs = range(0, 60) if len(K) > 1000 else range(len(K))
    results.append((*scan(K, offsets=offs, restarts=('none', 'segment')), name))
# page ring (restart per page, start at top-left, cw and ccw)
sys.path.insert(0, os.path.join(HERE, '..', 'liber-primus__circumference'))
import extract_circumference as ec
pg = ec.read_pages(); caps = ec.load_drop_caps()
for direction in ('cw', 'ccw'):
    keyarr = np.zeros(len(C), int); pos = 0
    # build a per-position key: the ring of the rune's own page, cycled from the page start
    page_ring = {}
    for n in sorted(set(PAGE.tolist())):
        rr = [IDX[pg[n][i][j]] for side in ec.ring(pg[n], caps.get(n, [])) for i, j in side if pg[n][i][j] in IDX]
        page_ring[n] = rr if direction == 'cw' else rr[::-1]
    pidx = np.zeros(len(C), int)
    for i in range(1, len(C)): pidx[i] = 0 if PAGE[i] != PAGE[i - 1] else pidx[i - 1] + 1
    Kpos = np.array([page_ring[PAGE[i]][pidx[i] % len(page_ring[PAGE[i]])] for i in range(len(C))])
    # use positional key directly (offset 0); key value for position i is Kpos[i]
    best = (0, None)
    for op in ('add28', 'sub28', 'mul29', 'imul29'):
        s = (C[1:] - C[:-1]) % 29; nz = s != 0; k = Kpos[1:]
        sv, kv = s[nz], k[nz]
        x = {'add28': 1 + ((sv - 1) - kv) % 28, 'sub28': 1 + ((sv - 1) + kv) % 28,
             'mul29': sv * INV29[kv % 28 + 1] % 29, 'imul29': sv * (kv % 28 + 1) % 29}[op]
        v = ioc28(x)
        if v > best[0]: best = (v, (op, 'positional', 'restart page', direction))
    results.append((*best, f'page ring ({direction})'))
results.sort(key=lambda r: -r[0])
for v, cfg, name in results[:10]: print(f'   {v:.4f}  {name:34s} {cfg}')
print('   ...lowest best: %.4f' % results[-1][0])
print('noise: best of ~%d settings per candidate on random data is about 1.003-1.005' % (4 * 2 * 2 * 60))
