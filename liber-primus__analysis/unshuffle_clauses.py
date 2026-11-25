"""Is the word order inside clauses a fixed (unkeyed) rearrangement we can undo? For each candidate permutation family
(defined for any clause length n), apply its INVERSE to every unsolved clause and measure the recovered word-length
sequence: lag-1 correlation (English -0.13), mutual information (English 0.04-0.05 bits), mean length of clause-final
and clause-initial words (English ~5.5 and ~3.8 runes letter by letter). Compare with the same statistics after
random within-clause shuffles (null) and with English (Blake, letter by letter). Also: are words inside clauses sorted
by length, GP sum or first rune (mean Kendall tau of word index vs that key)?"""
import os, sys, re, collections, itertools
import numpy as np
from scipy.stats import kendalltau
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import UNS, VAL
cls = collections.OrderedDict()
for r in UNS: cls.setdefault(r['clause'], collections.OrderedDict()).setdefault(r['word'], []).append(r['c'])
CL = [list(c.values()) for c in cls.values()]            # clause -> list of words (rune lists), in written order
def rail(n, k):                                          # rail-fence reading order of plaintext indices
    if k < 2 or n < 2: return list(range(n))
    cyc = 2 * (k - 1); rows = [[] for _ in range(k)]
    for i in range(n): p = i % cyc; rows[p if p < k else cyc - p].append(i)
    return [i for r in rows for i in r]
def columnar(n, k): return sorted(range(n), key=lambda i: (i % k, i))
def riffle(n, inn): h = (n + 1) // 2; a, b = list(range(h)), list(range(h, n)); out = []
def riffle(n, inn):
    h = n // 2 if inn else (n + 1) // 2; a, b = (list(range(h, n)), list(range(h))) if inn else (list(range(h)), list(range(h, n)))
    out = []
    for x, y in itertools.zip_longest(a, b):
        if x is not None: out.append(x)
        if y is not None: out.append(y)
    return out
def outside_in(n):
    out, lo, hi = [], 0, n - 1
    while lo <= hi:
        out.append(lo); lo += 1
        if lo <= hi: out.append(hi); hi -= 1
    return out
def half_rev(n): h = n // 2; return list(range(h))[::-1] + list(range(h, n))[::-1]
FAM = {'identity': lambda n: list(range(n)), 'reverse': lambda n: list(range(n))[::-1], 'outside-in': outside_in,
       'half-reverse': half_rev, 'riffle out': lambda n: riffle(n, False), 'riffle in': lambda n: riffle(n, True)}
for k in range(2, 7): FAM[f'rail fence {k}'] = (lambda k: lambda n: rail(n, k))(k)
for k in range(2, 9): FAM[f'columnar {k}'] = (lambda k: lambda n: columnar(n, k))(k)
def recover(perm_fn, inverse):
    out = []
    for c in CL:
        n = len(c); p = perm_fn(n)
        # written[j] = plain[p[j]]  ->  plain = written placed back at p;   'inverse' tries the other direction
        if not inverse: plain = [None] * n; [plain.__setitem__(p[j], c[j]) for j in range(n)]
        else: plain = [c[p[j]] for j in range(n)]
        out.append([len(w) for w in plain])
    return out
def acf1(x): x = np.asarray(x, float) - np.mean(x); return (x[1:] * x[:-1]).sum() / (x * x).sum()
def mi(x):
    x = np.minimum(np.asarray(x), 8); j = np.zeros((9, 9)); np.add.at(j, (x[:-1], x[1:]), 1); j /= j.sum()
    pa, pb = j.sum(1), j.sum(0); m = j > 0; return (j[m] * np.log2(j[m] / np.outer(pa, pb)[m])).sum()
def stats(cl):
    seq = [x for c in cl for x in c]
    return acf1(seq), mi(seq), np.mean([c[-1] for c in cl if len(c) >= 3]), np.mean([c[0] for c in cl if len(c) >= 3])
rng = np.random.default_rng(9)
nul = np.array([stats([list(rng.permutation([len(w) for w in c])) for c in CL]) for _ in range(400)])
mu, sd = nul.mean(0), nul.std(0)
print(f'English (Blake letter by letter): lag1 -0.126, MI 0.055, last-word 5.49, first-word 3.78')
print(f'within-clause random shuffle null: lag1 {mu[0]:+.3f}+/-{sd[0]:.3f}  MI {mu[1]:.4f}+/-{sd[1]:.4f}  last {mu[2]:.2f}+/-{sd[2]:.2f}  first {mu[3]:.2f}+/-{sd[3]:.2f}\n')
print(f'{"candidate":24s} {"dir":4s} {"lag1":>7s} {"z":>6s} {"MI":>7s} {"z":>6s} {"last":>5s} {"z":>6s} {"first":>5s} {"z":>6s}')
rows = []
for name, f in FAM.items():
    for inv in (False, True):
        if name in ('identity', 'reverse', 'half-reverse') and inv: continue
        s = stats(recover(f, inv)); z = (s - mu) / sd; rows.append((name, inv, s, z))
        print(f'{name:24s} {"inv" if inv else "fwd":4s} {s[0]:+7.3f} {z[0]:+6.2f} {s[1]:7.4f} {z[1]:+6.2f} {s[2]:5.2f} {z[2]:+6.2f} {s[3]:5.2f} {z[3]:+6.2f}')
eng_score = lambda z: -z[0] + z[1] + z[2] - z[3]          # direction of English: lag1 down, MI up, last up, first down
best = max(rows, key=lambda r: eng_score(r[3])); print(f'\nmost English-like: {best[0]} ({"inv" if best[1] else "fwd"}), combined z {eng_score(best[3]):.2f}')
nulls_comb = [eng_score((s - mu) / sd) for s in nul]; print(f'null combined z: 95th pct {np.percentile(nulls_comb, 95):.2f}, max {max(nulls_comb):.2f}  (one candidate of {len(rows)})')
print('\nare words sorted inside clauses? mean Kendall tau of word index vs key (clauses with >= 5 words):')
for kname, key in (('length', lambda w: len(w)), ('GP sum', lambda w: sum(VAL[x] for x in w)), ('first rune', lambda w: w[0]), ('last rune', lambda w: w[-1])):
    taus = [kendalltau(range(len(c)), [key(w) for w in c])[0] for c in CL if len(c) >= 5]
    taus = [t for t in taus if not np.isnan(t)]; print(f'   {kname:10s} tau {np.mean(taus):+.3f} +/- {np.std(taus) / np.sqrt(len(taus)):.3f}  ({len(taus)} clauses)')
