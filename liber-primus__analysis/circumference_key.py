"""'Shed our own circumferences' / 'the key is all around you' as key hypotheses, on the unsolved pages.
(1) page ring: the outer ring of runes (clockwise from top-left, drop caps on the left edge) is the key;
    shed it and decrypt the interior with it (all 8 start corners/directions, cyclic, +/-), raw and autokey-removed.
(2) word ring: first+last rune of each word; shed them and test the middles; or key the middles with them.
(3) circle: digits of pi and 2*pi (base 10, and base 29) as a running key.
Score: IoC (random 1.00, English ~1.73)."""
import os, sys, json, collections
import numpy as np
sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'liber-primus__circumference'))
import extract_circumference as ec
GP = ec.RUNES; IDX = {r: i for i, r in enumerate(GP)}
pages = ec.read_pages()
caps = ec.load_drop_caps()
def ioc(x, m=29):
    x = np.asarray(x) % m; cnt = np.bincount(x, minlength=m); n = len(x)
    return (cnt * (cnt - 1)).sum() / (n * (n - 1)) * m
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
unsolved_pages = sorted({p['page'] for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15})
# ---- (1) page ring as key for the interior ----
res = []
inter_all, ring_all = {}, {}
for n in unsolved_pages:
    rows = pages[n]
    rpos = [pos for side in ec.ring(rows, caps.get(n, [])) for pos in side]
    ring = [rows[i][j] for i, j in rpos]
    rset = set(rpos)
    interior = [rows[i][j] for i in range(len(rows)) for j in range(len(rows[i])) if (i, j) not in rset]
    ring = [IDX[x] for x in ring if x in IDX]; interior = [IDX[x] for x in interior if x in IDX]
    if len(ring) > 5 and len(interior) > 20: ring_all[n] = ring; inter_all[n] = interior
def variants(ring):
    L = len(ring)
    for start in range(L):                      # every start point, both directions
        yield 'cw', start, ring[start:] + ring[:start]
        r = ring[::-1]; yield 'ccw', start, r[start:] + r[:start]
best = []
for direction in ('cw', 'ccw'):
    for op in (1, -1):
        for target in ('raw', 'autokey removed'):
            # same rule on every page: start at the ring's first rune (top-left) going cw or ccw
            out = []
            for n, interior in inter_all.items():
                ring = ring_all[n] if direction == 'cw' else ring_all[n][::-1]
                t = np.array(interior); 
                if target == 'autokey removed': t = (t[1:] - t[:-1]) % 29
                k = np.array([ring[i % len(ring)] for i in range(len(t))])
                out.append((t - op * k) % 29)
            best.append((ioc(np.concatenate(out)), f'ring {direction} from top-left, {"subtract" if op > 0 else "add"}, {target}'))
# per-page best start (looks for any page that decrypts)
page_hits = []
for n, interior in inter_all.items():
    t0 = np.array(interior); bestp = (0, None)
    for direction, start, ring in variants(ring_all[n]):
        k = np.array([ring[i % len(ring)] for i in range(len(t0))])
        for op in (1, -1):
            v = ioc((t0 - op * k) % 29)
            if v > bestp[0]: bestp = (v, (direction, start, op))
    page_hits.append((bestp[0], n, len(t0), bestp[1]))
page_hits.sort(reverse=True)
print('(1) page ring as key for the interior')
for v, name in sorted(best, reverse=True)[:4]: print(f'    {v:.4f}  {name}')
print('    best single pages (any start/direction/sign):', [(round(v, 3), f'p{n}', L) for v, n, L, _ in page_hits[:5]])
# noise for per-page best-of-many: shuffle interiors
rng = np.random.default_rng(0); null = []
for n, interior in list(inter_all.items())[:15]:
    t0 = rng.permutation(np.array(interior)); bp = 0
    for direction, start, ring in variants(ring_all[n]):
        k = np.array([ring[i % len(ring)] for i in range(len(t0))])
        for op in (1, -1): bp = max(bp, ioc((t0 - op * k) % 29))
    null.append(bp)
print('    same search on shuffled interiors (15 pages): best per page median %.3f, max %.3f' % (np.median(null), max(null)))
ri = np.concatenate([np.array(v) for v in inter_all.values()]); rr = np.concatenate([np.array(v) for v in ring_all.values()])
print('    shed the ring: interior IoC %.4f (n=%d), ring IoC %.4f (n=%d)' % (ioc(ri), len(ri), ioc(rr), len(rr)))
# ---- (2) word ring ----
words, cur = [], None
for p in d['pages']:
    for l in p['lines']:
        if not 7 <= l['s'] <= 15: continue
        for t in l['t']:
            if t[0] in '-.': cur = None; continue
            if t[0] != 'r': cur = None; continue
            if cur is None: cur = []; words.append(cur)
            cur.append(IDX[t[1]])
mid = [x for w in words if len(w) > 2 for x in w[1:-1]]
edge = [x for w in words for x in ([w[0], w[-1]] if len(w) > 1 else [w[0]])]
print('\n(2) word rings: middles IoC %.4f (n=%d), first+last IoC %.4f (n=%d)' % (ioc(mid), len(mid), ioc(edge), len(edge)))
wk = []
for op in (1, -1):
    for keyname, kf in (('first rune', lambda w: [w[0]]), ('last rune', lambda w: [w[-1]]), ('first+last', lambda w: [w[0], w[-1]]), ('sum first+last', lambda w: [(w[0] + w[-1]) % 29])):
        out = []
        for w in words:
            if len(w) < 3: continue
            k = kf(w); m = w[1:-1]
            out += [(x - op * k[i % len(k)]) % 29 for i, x in enumerate(m)]
        wk.append((ioc(out), f'middle runes keyed by {keyname}, {"subtract" if op > 0 else "add"}'))
for v, name in sorted(wk, reverse=True)[:3]: print(f'    {v:.4f}  {name}')
# ---- (3) pi / 2pi ----
def pi_digits(n):            # Machin, integer arithmetic
    def arctan_inv(x, unity):
        s = t = unity // x; x2 = x * x; k = 3; sign = -1
        while t: t //= x2; s += sign * (t // k); sign = -sign; k += 2
        return s
    unity = 10 ** (n + 10)
    pi = 4 * (4 * arctan_inv(5, unity) - arctan_inv(239, unity))
    return pi, unity
PI, UNITY = pi_digits(22000)
def digits_base(x_int, unity, base, count):
    whole = x_int // unity; frac = x_int - whole * unity; out = []
    for _ in range(count):
        frac *= base; dgt = frac // unity; out.append(int(dgt)); frac -= dgt * unity
    return whole, out
c_all = np.array([IDX[t[1]] for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r'])
dd = (c_all[1:] - c_all[:-1]) % 29
pi10 = [int(ch) for ch in str(PI // 10 ** 10)][:20000]
tau10 = [int(ch) for ch in str(2 * PI // 10 ** 10)][:20000]
_, pi29 = digits_base(PI, UNITY, 29, 14000); _, tau29 = digits_base(2 * PI, UNITY, 29, 14000)
pk = []
for kname, K in (('pi base 10', pi10), ('2pi base 10', tau10), ('pi base 29', [3] + pi29), ('2pi base 29', [6] + tau29)):
    K = np.array(K)
    for tname, T in (('raw', c_all), ('autokey removed', dd)):
        for op in (1, -1):
            for off in range(0, 200):
                pk.append((ioc((T - op * K[off:off + len(T)]) % 29), kname, tname, op, off))
pk.sort(reverse=True)
print('\n(3) circle constants as running key (%d tests, offsets 0-199):' % len(pk))
for v, k, t, op, off in pk[:4]: print(f'    {v:.4f}  {k} | {t} | {"subtract" if op > 0 else "add"} | offset {off}')
print('    baselines: raw %.4f, autokey removed %.4f' % (ioc(c_all), ioc(dd)))
# ---- check the best single pages against a per-page null and show the decryption ----
LAT = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
print('\nper-page check of the top hits:')
for v, n, L, (direction, start, op) in page_hits[:3]:
    t0 = np.array(inter_all[n]); nulls = []
    for _ in range(300):
        ts = rng.permutation(t0); bp = 0
        for dname, s, ring in variants(ring_all[n]):
            k = np.array([ring[i % len(ring)] for i in range(len(ts))])
            for o in (1, -1): bp = max(bp, ioc((ts - o * k) % 29))
        nulls.append(bp)
    ring = ring_all[n] if direction == 'cw' else ring_all[n][::-1]; ring = ring[start:] + ring[:start]
    k = np.array([ring[i % len(ring)] for i in range(len(t0))]); pt = (t0 - op * k) % 29
    print(f'  p{n}: best IoC {v:.3f} on {L} runes; shuffled interiors reach >= that in {np.mean(np.array(nulls) >= v):.0%} of 300 runs')
    print('     decryption:', '-'.join(LAT[x] for x in pt))
