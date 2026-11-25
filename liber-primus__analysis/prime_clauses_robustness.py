"""Robustness of the unsolved short-clause prime excess: by part (LP1/LP2 pages, segment ranges, each segment),
by word-count definition of 'short', and by position (first clause of a paragraph vs elsewhere)."""
import os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
exec(open(os.path.join(HERE, 'prime_clauses_channels.py')).read().split("S = [r for r in R")[0])
short = lambda n: n <= 31
for lab, sel in (('LP1 unsolved (pages <=57)', lambda r: r['page'] <= 57), ('LP2 unsolved (pages >=58)', lambda r: r['page'] >= 58),
                 ('segments 7-11', lambda r: r['seg'] <= 11), ('segments 12-15', lambda r: r['seg'] >= 12)):
    n, real, mu, z, p = clause_test([r for r in UNS if sel(r)], 'c', short, reps=3000)
    print(f'{lab:28s} short clauses {n:3d}  prime {real:3d}  null {mu:5.1f}  z {z:5.2f}  p {p:.4f}')
cl = collections.OrderedDict()
for r in UNS: cl.setdefault(r['clause'], []).append(r)
x = np.array([r['c'] for r in UNS]); g = np.array([r['clause'] for r in UNS]); st = np.r_[0, np.nonzero(g[1:] != g[:-1])[0] + 1]
nw = np.array([len(set(r['word'] for r in rs)) for rs in cl.values()])
for W in (3, 4, 5, 6, 8):
    m = nw <= W; f = lambda y: isp[np.add.reduceat(V[y], st)][m].sum(); real = f(x); nul = np.array([f(rng.permutation(x)) for _ in range(3000)])
    print(f'<= {W} words: n={m.sum():3d} prime {real:3d} null {nul.mean():5.1f} z {(real - nul.mean()) / nul.std():5.2f} p {np.mean(nul >= real):.4f}')
first = set(); seen = set()
for rs in cl.values():
    if (rs[0]['seg'], rs[0]['para']) not in seen: seen.add((rs[0]['seg'], rs[0]['para'])); first.add(rs[0]['clause'])
for lab, cond in (('first clause of a paragraph', lambda c: c in first), ('elsewhere', lambda c: c not in first)):
    cs = [rs for k, rs in cl.items() if len(rs) <= 31 and cond(k)]
    print(f'{lab:28s} short clauses {len(cs):3d}, prime {sum(isp[V[[r["c"] for r in rs]].sum()] for rs in cs)}')
