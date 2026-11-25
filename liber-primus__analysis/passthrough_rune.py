"""Which rune, if any, passes through unencrypted? Model A: rune X passes through, all other plaintext runes encrypt
uniformly over all 29 -> freq(X) = f_X + (1 - f_X)/29, others (1 - f_X)/29. Model B: encrypted runes never land on X
(mod-28 style) -> freq(X) = f_X, others (1 - f_X)/28. f_X = English frequency of X (solved LP plaintext; also English
spelled letter by letter). For each X: log-likelihood of the observed counts vs the uniform model (positive = X fits
better than 'no pass-through'), and X's own z. Whole unsolved text and per section."""
import os, sys, re
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, UNS, d, LAT
sol = np.array([r['p'] for r in R if d['segments'][r['seg']]['solved']])
fLP = np.bincount(sol, minlength=29) / len(sol)
exec(open(os.path.join(HERE, 'sum_preserving.py')).read().split("def stats")[0].split("uns = words")[0])
L2I = {k: i for i, k in enumerate(LAT)}
src = open(os.path.join(HERE, 'sum_preserving.py')).read()
exec(src[src.index('L2I = {'):src.index('def stats')])
fLL = np.bincount(np.concatenate([w for w in bl_n if w]), minlength=29) / sum(len(w) for w in bl_n)
def ll(cnt, p): return (cnt * np.log(p)).sum()
def table(c, label):
    cnt = np.bincount(c, minlength=29); n = cnt.sum(); base = ll(cnt, np.full(29, 1 / 29))
    print(f'\n== {label}: {n} runes')
    for fname, f in (('LP spelling', fLP), ('letter-by-letter', fLL)):
        res = []
        for X in range(29):
            if f[X] == 0: continue
            pA = np.full(29, (1 - f[X]) / 29); pA[X] = f[X] + (1 - f[X]) / 29
            pB = np.full(29, (1 - f[X]) / 28); pB[X] = f[X]
            res.append((ll(cnt, pA) - base, ll(cnt, pB) - base, X))
        best = sorted(res, reverse=True)[:4]; bestB = sorted(res, key=lambda r: -r[1])[:4]
        print(f'  [{fname}] model A best:', ', '.join(f'{LAT[X]} (f={f[X]:.3f}, obs {cnt[X] / n:.3f}, dLL {a:+.1f})' for a, b, X in best))
        print(f'  [{fname}] model B best:', ', '.join(f'{LAT[X]} (f={f[X]:.3f}, obs {cnt[X] / n:.3f}, dLL {b:+.1f})' for a, b, X in bestB))
C = np.array([r['c'] for r in UNS]); seg = np.array([r['seg'] for r in UNS])
table(C, 'all unsolved, raw ciphertext')
D = (C[1:] - C[:-1]) % 29; table(D[seg[1:] == seg[:-1]], 'all unsolved, autokey-removed stream')
for s in range(7, 16): table(C[seg == s], f'segment {s}, raw ciphertext')
