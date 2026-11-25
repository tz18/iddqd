"""(1) Prime clause sums: solved plaintext, split into short (<= 31 runes, maxim-like) and long clauses; the unsolved
ciphertext for comparison. Null: runes shuffled within the text, clause lengths kept.
(2) 'Prisoner' channels left open by the constraints: the word-length sequence (visible, unencrypted). Compare
the unsolved word-length distribution and its lag-1 correlation with the solved plaintext's (English in runes)."""
import os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, VAL, d, PR, UNS
isp = np.zeros(400000, bool); isp[PR] = True; V = np.array(VAL); rng = np.random.default_rng(5)
def clause_test(rs, field, sel=lambda n: True, reps=4000):
    x = np.array([r[field] for r in rs]); g = np.array([r['clause'] for r in rs])
    st = np.r_[0, np.nonzero(g[1:] != g[:-1])[0] + 1]; ln = np.diff(np.r_[st, len(x)]); m = np.array([sel(n) for n in ln])
    f = lambda y: isp[np.add.reduceat(V[y], st)][m].sum()
    real = f(x); nul = np.array([f(rng.permutation(x)) for _ in range(reps)])
    return m.sum(), real, nul.mean(), (real - nul.mean()) / nul.std(), np.mean(nul >= real)
S = [r for r in R if d['segments'][r['seg']]['solved']]
for lab, sel in (('all clauses', lambda n: True), ('short clauses (<=31 runes)', lambda n: n <= 31), ('long clauses (>31 runes)', lambda n: n > 31)):
    for fld in ('p', 'c'):
        n, real, mu, z, p = clause_test(S, fld, sel)
        print(f'solved {"pt" if fld == "p" else "ct"} {lab:28s} n={n:3d} prime {real:3d}  null {mu:5.1f}  z {z:5.2f}  p {p:.4f}')
for lab, sel in (('all clauses', lambda n: True), ('short clauses (<=31 runes)', lambda n: n <= 31)):
    n, real, mu, z, p = clause_test(UNS, 'c', sel)
    print(f'UNSOLVED ct {lab:28s} n={n:3d} prime {real:3d}  null {mu:5.1f}  z {z:5.2f}  p {p:.4f}')
def wl(rs):
    c = collections.Counter(r['word'] for r in rs); ws = sorted(c); return np.array([c[w] for w in ws])
a, b = wl(S), wl(UNS)
print('\nword lengths in runes: solved pt mean %.2f sd %.2f | unsolved mean %.2f sd %.2f' % (a.mean(), a.std(), b.mean(), b.std()))
K = np.arange(1, 15); ca = np.array([(np.minimum(a, 14) == k).sum() for k in K]); cb = np.array([(np.minimum(b, 14) == k).sum() for k in K])
print('  share by length 1..14+:'); print('   solved  ', ' '.join(f'{v:.3f}' for v in ca / ca.sum())); print('   unsolved', ' '.join(f'{v:.3f}' for v in cb / cb.sum()))
tab = np.array([ca, cb]); e = tab.sum(1, keepdims=True) * tab.sum(0) / tab.sum(); chi = ((tab - e) ** 2 / np.maximum(e, 1e-9)).sum()
print(f'  chi2 (13 df) = {chi:.1f}  (13 expected if same distribution)')
def lag1(x): x = x - x.mean(); return (x[1:] * x[:-1]).sum() / (x * x).sum()
nb = [lag1(rng.permutation(b)) for _ in range(2000)]
print(f'  lag-1 correlation of word lengths: solved {lag1(a):.3f}, unsolved {lag1(b):.3f} (shuffled unsolved {np.mean(nb):.3f} +/- {np.std(nb):.3f})')
# English reference: Blake's MHH in rune counts (TH NG ING EA OE AE IO IA EO as one rune)
import re
def rcount(w):
    w = re.sub('[^A-Z]', '', w.upper())
    for g in ('ING', 'TH', 'NG', 'EA', 'OE', 'AE', 'IO', 'IA', 'EO'): w = w.replace(g, '#')
    return len(w.replace('QU', 'CW'))
bl = np.array([rcount(w) for w in re.findall(r'[A-Za-z]+', open(os.path.join(HERE, 'sources', 'blake_marriage_of_heaven_and_hell.txt')).read())])
bl = bl[bl > 0]
print(f'  English reference (Blake MHH, {len(bl)} words): mean {bl.mean():.2f}, 2-rune share {np.mean(bl == 2):.3f}, lag-1 {lag1(bl):.3f}')
print(f'  unsolved: 2-rune share {np.mean(b == 2):.3f} (binomial SE {np.sqrt(.25 * .75 / len(b)):.3f}), lag-1 SE ~ {1 / np.sqrt(len(b)):.3f}')
