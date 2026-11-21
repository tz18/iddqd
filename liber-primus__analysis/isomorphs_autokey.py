"""Isomorph search and ciphertext-autokey test on the unsolved stream."""
import os, json, collections, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
PR = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
def stream_for(segs):
    return [IDX[t[1]] for p in d['pages'] for l in p['lines'] if l['s'] in segs for t in l['t'] if t[0] == 'r']
U = stream_for(range(7, 16))
rng = random.Random(7)

# ---------- isomorphs ----------
def pattern(w):
    m = {}; return tuple(m.setdefault(c, len(m)) for c in w)
def isomorphs(s, L, min_rep):
    """windows of length L whose repeat pattern has >= min_rep repeated positions, grouped by pattern"""
    groups = collections.defaultdict(list)
    for i in range(len(s) - L + 1):
        pt = pattern(s[i:i + L])
        if L - len(set(pt)) >= min_rep: groups[pt].append(i)
    return {k: v for k, v in groups.items() if len(v) > 1}
def shuffled_no_doublets(s):
    """null that keeps rune frequencies AND the doublet shortage: shuffle, then repair doublets by swaps"""
    a = s[:]; rng.shuffle(a)
    target = sum(a == b for a, b in zip(s, s[1:]))
    for _ in range(200000):
        dbl = [i for i in range(1, len(a)) if a[i] == a[i - 1]]
        if len(dbl) <= target: break
        i = rng.choice(dbl); j = rng.randrange(len(a)); a[i], a[j] = a[j], a[i]
    return a
print('isomorphs (repeat patterns shared by 2+ windows), real vs frequency+doublet-matched shuffles:')
for L, mr in ((8, 3), (10, 3), (12, 4), (15, 5), (20, 6)):
    real = isomorphs(U, L, mr); nr = sum(len(v) - 1 for v in real.values())
    nulls = [sum(len(v) - 1 for v in isomorphs(shuffled_no_doublets(U), L, mr).values()) for _ in range(8)]
    m = sum(nulls) / len(nulls); sd = (sum((x - m) ** 2 for x in nulls) / len(nulls)) ** .5
    print(f'  window {L}, >= {mr} repeats: real {nr}  shuffled {m:.1f} ± {sd:.1f}')
    if L == 12:
        best = sorted(real.items(), key=lambda kv: -len(kv[1]))[:3]
        for pt, pos in best:
            dists = [b - a for a, b in zip(pos, pos[1:])]
            print('    pattern', ''.join('abcdefghijklmnop'[x] for x in pt), 'at', pos[:6], 'distances', dists[:6])

# ---------- ciphertext autokey: d_i = c_i - c_{i-k} ----------
def ioc(xs):
    c = collections.Counter(xs); n = len(xs)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * 29   # 1.0 = random, plain runic English ~1.6-1.8
plain_ref = stream_for((2, 4, 6, 17))
print('\nreference IoC (x29): random 1.00, unsolved ct %.3f, plain-rune English %.3f' % (ioc(U), ioc(plain_ref)))
print('autokey difference streams d = c[i] ∓ c[i-k], IoC x29:')
best = []
for k in range(1, 41):
    for name, f in (('c-c', lambda a, b: (a - b) % 29), ('c+c', lambda a, b: (a + b) % 29)):
        ds = [f(U[i], U[i - k]) for i in range(k, len(U))]
        best.append((ioc(ds), k, name))
best.sort(reverse=True)
print('  highest:', [(f'{n} k={k}', round(v, 3)) for v, k, n in best[:5]], ' lowest:', [(f'{n} k={k}', round(v, 3)) for v, k, n in best[-3:]])
d1 = [(U[i] - U[i - 1]) % 29 for i in range(1, len(U))]
cnt = collections.Counter(d1)
print('  lag-1 difference histogram (0 = doublet):', [cnt[v] for v in range(29)])
# periodic (Vigenere-under-autokey) check: average column IoC of d1 for periods 1..40
pk = []
for per in range(1, 41):
    cols = [d1[j::per] for j in range(per)]
    pk.append((sum(ioc(c) for c in cols) / per, per))
pk.sort(reverse=True)
print('  d (lag 1) split into columns by period, best average column IoC:', [(f'p={p}', round(v, 3)) for v, p in pk[:5]])
# lag-1 difference minus classic LP key streams
primes = [];  n = 2
while len(primes) < len(d1) + 10:
    if all(n % q for q in primes if q * q <= n): primes.append(n)
    n += 1
fib = [0, 1]
while len(fib) < len(d1) + 10: fib.append((fib[-1] + fib[-2]) % 29)
for name, ks in (('primes', primes), ('totient(primes)', [p - 1 for p in primes]), ('fibonacci', fib), ('GP values of previous ct', [PR[c] for c in U])):
    for sgn in (1, -1):
        xs = [(d1[i] - sgn * ks[i]) % 29 for i in range(len(d1))]
        print(f'  d - {"+" if sgn>0 else "-"}{name}: IoC {ioc(xs):.3f}')
