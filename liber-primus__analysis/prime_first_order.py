"""Could words inside clauses be ordered by a plaintext property (prime word sums first/last, sum, product)?
Sum and product track word length (already tested: Kendall tau ~0). Primality tracks parity: 93% of prime-sum plaintext
words have odd length (solved LP). So 'prime-sum words first' would move odd-length words to the front of clauses.
Statistic: mean relative position (0 first .. 1 last) of odd- minus even-length words; null: within-clause shuffles;
reference: the same sort simulated on the solved plaintext clauses."""
import os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import UNS, R, d, VAL, PR
isp = set(PR)
def cl_of(rs, f):
    cls = collections.OrderedDict()
    for r in rs: cls.setdefault(r['clause'], collections.OrderedDict()).setdefault(r['word'], []).append(f(r))
    return [list(c.values()) for c in cls.values()]
def gap(cls):
    po, pe = [], []
    for c in cls:
        if len(c) < 3: continue
        for i, w in enumerate(c): (po if len(w) % 2 else pe).append(i / (len(c) - 1))
    return np.mean(po) - np.mean(pe)
sol = cl_of([r for r in R if d['segments'][r['seg']]['solved']], lambda r: r['p']); ws = [w for c in sol for w in c]
pr = np.array([sum(VAL[x] for x in w) in isp for w in ws]); odd = np.array([len(w) % 2 == 1 for w in ws])
print(f'solved plaintext: prime-sum words {pr.mean():.2f}; odd length among prime-sum {odd[pr].mean():.2f}, among others {odd[~pr].mean():.2f}')
U = cl_of(UNS, lambda r: r['c']); rng = np.random.default_rng(3)
real = gap(U); nul = [gap([list(rng.permutation(np.array(c, dtype=object))) for c in U]) for _ in range(2000)]
print(f'unsolved odd-minus-even position gap {real:+.4f} (null {np.mean(nul):+.4f} +/- {np.std(nul):.4f}, z {(real - np.mean(nul)) / np.std(nul):+.2f})')
for lab, rev in (('prime-sum words first', False), ('prime-sum words last', True)):
    sim = [sorted(c, key=lambda w: (sum(VAL[x] for x in w) in isp) == rev) for c in sol]
    print(f'simulated on solved clauses, {lab}: gap {gap(sim):+.3f}')
