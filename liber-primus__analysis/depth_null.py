"""Exact binomial tails for the top depth alignments, and the same search on shuffled pages (null for the max)."""
import os, json, math, collections
import numpy as np
from scipy.stats import binom
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'depth_search.py')).read()
exec(src.split('# expected coincidence')[0])
def search(Dd):
    OHd = {k: onehot(v) for k, v in Dd.items()}; best = []
    ks = list(Dd)
    for ai, a in enumerate(ks):
        for b in ks[ai:]:
            A, B = OHd[a], OHd[b]; la, lb = A.shape[1], B.shape[1]
            m = sum(np.correlate(A[s], B[s], mode='full') for s in range(29))
            offs = np.arange(-(lb - 1), la); ov = np.minimum(la, offs + lb) - np.maximum(0, offs)
            pe = float((A.mean(1) * B.mean(1)).sum())
            ok = (ov >= 60) & ((a != b) | (offs > 0))
            if not ok.any(): continue
            p = binom.sf(np.round(m[ok]) - 1, ov[ok], pe)   # P(X >= observed)
            i = int(np.argmin(p)); best.append((float(p[i]), a, b, int(offs[ok][i]), int(ov[ok][i]), int(round(m[ok][i]))))
    best.sort()
    return best
real = search(D)
print('real: smallest exact p-values:', [(f'{p:.1e}', a, b, o, ov, mm) for p, a, b, o, ov, mm in real[:5]])
rng = np.random.default_rng(8)
mins = []
for r in range(5):
    Ds = {k: rng.permutation(v) for k, v in D.items()}
    mins.append(search(Ds)[0][0])
print('shuffled pages (5 runs): smallest p-value in each run:', [f'{x:.1e}' for x in mins])
