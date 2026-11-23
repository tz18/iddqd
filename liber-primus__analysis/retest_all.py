"""Re-run every earlier 'peel' test with the structure battery instead of IoC, and keep all scores.
For each family, the identical scan is repeated with random keys (control); a family is interesting only if its
best score beats the control's best. All per-test scores are written to results/retest_<family>.csv.gz."""
import os, sys, json, gzip, math, zlib, hashlib, warnings, time, csv
import numpy as np
warnings.filterwarnings('ignore'); sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE, 'results')
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
PRV = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
rows = [(IDX[t[1]], l['s'], p['page']) for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
C = np.array([r[0] for r in rows]); SEG = np.array([r[1] for r in rows]); PAGE = np.array([r[2] for r in rows])
D = (C[1:] - C[:-1]) % 29; NZ = D[D != 0] - 1
def restart(g):
    idx = np.zeros(len(g), int)
    for i in range(1, len(g)): idx[i] = 0 if g[i] != g[i - 1] else idx[i - 1] + 1
    return idx
POS = {'whole': np.arange(len(C)), 'segment': restart(SEG), 'page': restart(PAGE)}
POSD = {k: v[1:] for k, v in POS.items()}
# ---------------- fast battery ----------------
def battery(x, m):
    x = np.asarray(x, dtype=np.int64) % m; n = len(x)
    cnt = np.bincount(x, minlength=m); e = n / m
    uni = (((cnt - e) ** 2).sum() / e - (m - 1)) / math.sqrt(2 * (m - 1))
    bg = np.bincount(x[:-1] * m + x[1:], minlength=m * m); eb = (n - 1) / (m * m)
    big = (((bg - eb) ** 2).sum() / eb - (m * m - 1)) / math.sqrt(2 * (m * m - 1))
    ar = np.arange(n); per = -9.0
    for P in range(2, 41):
        cc = np.bincount((ar % P) * m + x, minlength=P * m).reshape(P, m); k = cc.sum(1)
        v = ((cc * (cc - 1)).sum(1) / (k * (k - 1)) * m).mean()
        per = max(per, (v - 1) / (math.sqrt(2 * (m - 1)) / (n / P) / math.sqrt(P)))
    p = 1 / m; lag = []
    for k in range(1, 51):
        eq = int((x[:-k] == x[k:]).sum()); N = n - k; lag.append((eq - N * p) / math.sqrt(N * p * (1 - p)))
    h = x[:-4] * m ** 4 + x[1:-3] * m ** 3 + x[2:-2] * m ** 2 + x[3:-1] * m + x[4:]
    _, c5 = np.unique(h, return_counts=True); rep = int((c5 - 1).sum()); lam = (n - 4) ** 2 / 2 / m ** 5
    g5 = (rep - lam) / math.sqrt(lam + 1e-9)
    comp = len(zlib.compress(x.astype(np.uint8).tobytes(), 6)) if m <= 256 else 0
    return np.array([uni, big, per, max(abs(z) for z in lag[1:]), abs(lag[0]), g5, -comp], float)
NAMES = ['unigram', 'bigram', 'periodic IoC', 'lag repeats', 'doublets', '5-gram repeats', 'compressibility']
CAL = {}
def calib(m, n):
    key = (m, n)
    if key not in CAL:
        rng = np.random.default_rng(m * 100003 + n)
        B = np.array([battery(rng.integers(0, m, n), m) for _ in range(40)])
        CAL[key] = (B.mean(0), B.std(0) + 1e-9)
    return CAL[key]
def score(x, m):
    x = np.asarray(x); n = len(x)
    if n < 200: return 0.0, ''
    mu, sd = calib(m, (n // 500) * 500 or n)
    z = (battery(x, m) - mu) / sd; i = int(np.argmax(z)); return float(z[i]), NAMES[i]
# ---------------- families: each yields (label, peeled array, alphabet) for a given key source ----------------
def bytes_to_runes(b, red):
    b = np.frombuffer(b, np.uint8).astype(int)
    if red == 'mod29': return b % 29
    if red == 'mod28+1': return b % 28 + 1
    if red == 'reject232': return b[b < 232] % 29
    bits = np.unpackbits(np.frombuffer(b.astype(np.uint8).tobytes(), np.uint8)); n5 = len(bits) // 5
    return (bits[:n5 * 5].reshape(-1, 5) @ (1 << np.arange(4, -1, -1))) % 29
def additive(streams, offsets=(0,), schemes=('whole', 'segment', 'page')):
    """streams: dict name -> integer array; peel raw and autokey-removed text, both signs"""
    for sname, K in streams.items():
        for sch in schemes:
            for off in offsets:
                for tname, T, pos in (('raw', C, POS[sch]), ('autokey removed', D, POSD[sch])):
                    idx = (pos + off) % len(K); k = K[idx]
                    for op in (1, -1):
                        yield f'{sname}|{sch}|off{off}|{tname}|{"-" if op > 0 else "+"}', (T - op * k) % 29, 29
def cyclic_all_offsets(streams, targets=('raw', 'autokey removed', 'nz28')):
    for sname, K in streams.items():
        L = len(K)
        for tname in targets:
            T, m = {'raw': (C, 29), 'autokey removed': (D, 29), 'nz28': (NZ, 28)}[tname]
            ar = np.arange(len(T))
            for off in range(L):
                k = K[(ar + off) % L] % m
                for op in (1, -1):
                    yield f'{sname}|off{off}|{tname}|{"-" if op > 0 else "+"}', (T - op * k) % m, m
# key sources (real) and their random counterparts (control)
def primes_n(n):
    s = np.ones(400000, bool); s[:2] = False
    for i in range(2, 633):
        if s[i]: s[i * i::i] = False
    return np.nonzero(s)[0][:n]
PRIMES = primes_n(20000)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
try:
    from cryptography.hazmat.decrepit.ciphers import algorithms as old
except Exception:
    old = algorithms
def zero_key_streams(nb=40000):
    z = lambda n: bytes(n); out = {}
    for bits in (128, 192, 256):
        out[f'AES{bits}-CTR'] = Cipher(algorithms.AES(z(bits // 8)), modes.CTR(z(16))).encryptor().update(z(nb))
        out[f'AES{bits}-OFB'] = Cipher(algorithms.AES(z(bits // 8)), modes.OFB(z(16))).encryptor().update(z(nb))
    out['ChaCha20'] = Cipher(algorithms.ChaCha20(z(32), z(16)), None).encryptor().update(z(nb))
    out['SM4-CTR'] = Cipher(algorithms.SM4(z(16)), modes.CTR(z(16))).encryptor().update(z(nb))
    for kl in (5, 16, 32): out[f'RC4-{kl}'] = Cipher(old.ARC4(z(kl)), None).encryptor().update(z(nb))
    for nm, alg, kl, bl in (('3DES', 'TripleDES', 24, 8), ('Blowfish', 'Blowfish', 16, 8), ('CAST5', 'CAST5', 16, 8), ('IDEA', 'IDEA', 16, 8), ('SEED', 'SEED', 16, 16)):
        A = getattr(old, alg, None)
        if A: out[f'{nm}-OFB'] = Cipher(A(z(kl)), modes.OFB(z(bl))).encryptor().update(z(nb))
    return out
def pi_streams():
    def at(x, u):
        s = t = u // x; x2 = x * x; k = 3; sg = -1
        while t: t //= x2; s += sg * (t // k); sg = -sg; k += 2
        return s
    u = 10 ** 21010; PI = 4 * (4 * at(5, u) - at(239, u))
    def base29(v):
        frac = v - (v // u) * u; out = []
        for _ in range(14000): frac *= 29; dg = frac // u; out.append(int(dg)); frac -= dg * u
        return np.array(out)
    return {'pi10': np.array([int(ch) for ch in str(PI // 10 ** 10)][:20000]), '2pi10': np.array([int(ch) for ch in str(2 * PI // 10 ** 10)][:20000]),
            'pi29': base29(PI), '2pi29': base29(2 * PI)}
W = open(os.path.join(HERE, '..', '2013', '02', 'wisdom'), 'rb').read()
def wisdom_streams(wb):
    b = np.frombuffer(wb, np.uint8).astype(int); bits = np.unpackbits(np.frombuffer(wb, np.uint8))
    def b29(order):
        n = int.from_bytes(wb, order); o = []
        while n: n, r = divmod(n, 29); o.append(r)
        return np.array(o[::-1])
    return {'mod29': b % 29, 'mod28+1': b % 28 + 1, 'reject232': b[b < 232] % 29,
            '5bit': (bits[:len(bits) // 5 * 5].reshape(-1, 5) @ (1 << np.arange(4, -1, -1))) % 29,
            'b29be': b29('big'), 'b29le': b29('little')}
def other_peels(rand=None):
    """smaller families: exponent/multiplier, fixed-zero layers, RSA modes, progressive keys, ring/word ring,
    rune-selection rules, deconvolution kernels. rand: rng to replace keys by random ones (control)"""
    from math import gcd
    inv28 = lambda e: pow(int(e) % 28, -1, 28) if gcd(int(e) % 28, 28) == 1 else None
    def expo(c, e):
        dd = inv28(e); return pow(int(c), dd, 29) if dd is not None else int(c)
    def mul(c, e):
        e = int(e) % 29; return int(c) * pow(e, -1, 29) % 29 if e else int(c)
    R = (lambda n: rand.integers(1, 10 ** 6, n)) if rand is not None else None
    streams = {'prev ct GP': np.r_[1, [PRV[x] for x in C[:-1]]], 'prev ct index': np.r_[1, C[:-1]], 'ith prime': PRIMES[:len(C)]}
    for nm, K in streams.items():
        K = R(len(C)) if R else K
        yield f'exp|{nm}', np.array([expo(c, k) for c, k in zip(C, K)]), 29
        yield f'mul|{nm}', np.array([mul(c, k) for c, k in zip(C, K)]), 29
    # fixed-zero inner layers on the autokey-removed stream
    for nm, K in (('primes', PRIMES % 29), ('totient', (PRIMES - 1) % 29), ('position+1', (np.arange(20000) + 1) % 29)):
        K = (R(20000) % 28 + 1) if R else np.where(K % 29 == 0, 1, K)
        yield f'fixedzero mul|{nm}', np.array([dd * pow(int(K[i]) % 29 or 1, -1, 29) % 29 for i, dd in enumerate(D)]), 29
    # RSA-style chaining modes, all exponents
    for e in [x for x in range(1, 28) if gcd(x, 28) == 1]:
        ee = (int(R(1)[0]) % 28) if R else e
        if gcd(ee, 28) != 1: ee = 1
        dd = pow(ee, -1, 28)
        yield f'CBC+|e{e}', np.array([(pow(int(C[i]), dd, 29) - C[i - 1]) % 29 for i in range(1, len(C))]), 29
        yield f'CFB+|e{e}', np.array([(C[i] - pow(int(C[i - 1]), ee, 29)) % 29 for i in range(1, len(C))]), 29
    # progressive keys (constant step)
    for step in range(1, 29):
        st = int(R(1)[0]) % 29 if R else step
        yield f'progressive|{step}', (C - st * np.arange(len(C))) % 29, 29
    # page ring as key for page interiors (top-left start, cw/ccw, both signs), and word ring
    sys.path.insert(0, os.path.join(HERE, '..', 'liber-primus__circumference'))
    import extract_circumference as ec
    pg = ec.read_pages(); caps = ec.load_drop_caps()
    for direction in ('cw', 'ccw'):
        for op in (1, -1):
            out = []
            for n in sorted(set(PAGE.tolist())):
                rows_ = pg[n]; rp = [pos for side in ec.ring(rows_, caps.get(n, [])) for pos in side]; rs = set(rp)
                ring = [IDX[rows_[i][j]] for i, j in rp if rows_[i][j] in IDX]
                inner = [IDX[rows_[i][j]] for i in range(len(rows_)) for j in range(len(rows_[i])) if (i, j) not in rs and rows_[i][j] in IDX]
                if len(ring) < 5 or not inner: continue
                if direction == 'ccw': ring = ring[::-1]
                if R: ring = list(R(len(ring)) % 29)
                out += [(x - op * ring[i % len(ring)]) % 29 for i, x in enumerate(inner)]
            yield f'page ring|{direction}|{op}', np.array(out), 29
    # deconvolution kernels (length <= 3, leading 1)
    for g1 in range(29):
        for g2 in range(29):
            a, b2 = (int(R(1)[0]) % 29, int(R(1)[0]) % 29) if R else (g1, g2)
            yield f'kernel|1,{g1},{g2}', (C[2:] + a * C[1:-1] + b2 * C[:-2]) % 29, 29
FAMILIES = {
    'zero-key keystreams': lambda rand: additive({f'{g}|{red}': (bytes_to_runes(ks, red) if rand is None else rand.integers(0, 29, 40000))
                                                  for g, ks in zero_key_streams().items() for red in ('mod29', 'mod28+1', 'reject232', '5bit')}),
    'pi digits': lambda rand: additive({k: (v if rand is None else rand.integers(0, 29, len(v))) for k, v in pi_streams().items()},
                                       offsets=range(0, 200), schemes=('whole',)),
    'totient/prime offsets': lambda rand: additive({'totient': ((PRIMES - 1) % 29 if rand is None else rand.integers(0, 29, 20000)),
                                                    'primes': (PRIMES % 29 if rand is None else rand.integers(0, 29, 20000))},
                                                   offsets=range(0, 3000)),
    'wisdom key': lambda rand: cyclic_all_offsets(wisdom_streams(W if rand is None else bytes(rand.integers(0, 256, len(W)).astype(np.uint8)))),
    'other peels': lambda rand: other_peels(rand),
}
def run(fam, rand=None, write=None):
    best = (-99, None); n = 0
    for label, x, m in FAMILIES[fam](rand):
        s, which = score(x, m); n += 1
        if write: write.writerow([label, f'{s:.3f}', which])
        if s > best[0]: best = (s, label, which)
    return best, n
if __name__ == '__main__':
    only = sys.argv[1:] or list(FAMILIES)
    summary = {}
    for fam in only:
        t0 = time.time()
        with gzip.open(os.path.join(RES, f'retest_{fam.replace(" ", "_").replace("/", "-")}.csv.gz'), 'wt') as fh:
            w = csv.writer(fh); w.writerow(['setting', 'structure_score', 'strongest_measure'])
            best, n = run(fam, None, w)
        ctrl = [run(fam, np.random.default_rng(1000 + r))[0][0] for r in range(2 if n < 20000 else 1)]
        summary[fam] = dict(tests=n, best=best[0], best_setting=best[1], measure=best[2], control_best=ctrl)
        print(f'{fam:24s} tests {n:7d}  best {best[0]:6.2f} ({best[2]}) at {best[1]}   control best {[round(c, 2) for c in ctrl]}   [{time.time()-t0:.0f}s]', flush=True)
    json.dump(summary, open(os.path.join(RES, 'retest_summary_' + '_'.join(f.replace(' ', '_').replace('/', '-') for f in only) + '.json'), 'w'), indent=1)
