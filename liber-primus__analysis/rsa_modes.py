"""RSA-style exponent permutation on single runes, chained like block-cipher modes.
E(x) = x^e mod 29, D(y) = y^d mod 29, e*d = 1 mod 28.
  CBC-like: c[i] = E(p[i] + c[i-1])   ->  p[i] = D(c[i]) - c[i-1]   (also the '-' and '*' variants)
  CFB-like: c[i] = p[i] + E(c[i-1])   ->  p[i] = c[i] - E(c[i-1])
For each, the doublet rate English would produce is (1/29) * sum_c P_english(f(c)), where f(c) is the
plaintext rune that makes c[i] == c[i-1]. We look for modes predicting ~0.66% and decrypting to IoC ~1.7."""
import os, re, json, collections
from math import gcd
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'progressive_key.py')).read().split('dp = [')[0])   # English sample P (rune indices)
eng = collections.Counter(P); ne = len(P); pe = {k: eng[k] / ne for k in range(29)}
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
IDX = {r: i for i, r in enumerate(GP)}
U = [IDX[t[1]] for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
def ioc(xs):
    c = collections.Counter(xs); n = len(xs); return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * 29
inv29 = lambda x: pow(x, -1, 29)
rows = []
for e in [x for x in range(1, 28) if gcd(x, 28) == 1]:
    dd = pow(e, -1, 28)
    E = lambda x: pow(x, e, 29); D = lambda y: pow(y, dd, 29)
    modes = {
        'CBC +  c=E(p+prev)':  (lambda c, pv: (D(c) - pv) % 29,          lambda pv: (D(pv) - pv) % 29),
        'CBC -  c=E(p-prev)':  (lambda c, pv: (D(c) + pv) % 29,          lambda pv: (D(pv) + pv) % 29),
        'CBC -2 c=E(prev-p)':  (lambda c, pv: (pv - D(c)) % 29,          lambda pv: (pv - D(pv)) % 29),
        'CFB +  c=p+E(prev)':  (lambda c, pv: (c - E(pv)) % 29,          lambda pv: (pv - E(pv)) % 29),
        'CFB -  c=E(prev)-p':  (lambda c, pv: (E(pv) - c) % 29,          lambda pv: (E(pv) - pv) % 29),
        'CBC *  c=E(p*prev)':  (lambda c, pv: D(c) * inv29(pv) % 29 if pv else D(c), lambda pv: D(pv) * inv29(pv) % 29 if pv else 0),
    }
    for name, (decf, f) in modes.items():
        pred = sum(pe[f(c)] for c in range(29)) / 29
        pt = [decf(U[i], U[i - 1]) for i in range(1, len(U))]
        rows.append((abs(pred - 0.0066), e, name, pred, ioc(pt)))
rows.sort()
print('English sample %d runes; observed unsolved doublet rate 0.66%%' % ne)
print('closest predicted doublet rates (mode, exponent) and IoC of the decryption:')
for _, e, name, pred, v in rows[:10]: print(f'   e={e:2d}  {name:20s} predicts {pred*100:.2f}%   decrypts to IoC {v:.3f}')
print('best IoC over all %d mode/exponent pairs: %.3f' % (len(rows), max(r[4] for r in rows)))
