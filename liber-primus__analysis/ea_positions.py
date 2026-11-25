"""If a ciphertext doublet (c[i] == c[i-1]) marks plaintext EA at position i, the doublets must sit where EA sits in
English words. Compare the doublets' (word length, position in word) with EA in English spelled with LP runes
(Blake's MHH + the solved LP plaintext). Also: impossible spots (1-rune words) and consecutive doublets (EA EA).
Null: where a uniformly random position would fall (the unsolved word layout)."""
import os, sys, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, UNS, LAT, d
src = open(os.path.join(HERE, 'sum_preserving.py')).read()
exec(src[src.index('L2I = {'):src.index('def stats')])
EA = LAT.index('EA')
def where(words, test):
    out = collections.Counter()
    for w in words:
        for i, x in enumerate(w):
            if test(w, i): out[(len(w), 'initial' if i == 0 else 'final' if i == len(w) - 1 else 'medial')] += 1
    return out
sol = collections.OrderedDict()
for r in R:
    if d['segments'][r['seg']]['solved']: sol.setdefault(r['word'], []).append(r['p'])
eng = [w for w in bl_d if w] + list(sol.values())
E = where(eng, lambda w, i: w[i] == EA)
uw = collections.OrderedDict()
for r in UNS: uw.setdefault(r['word'], []).append(r)
# doublet at rune i: same ciphertext as previous rune in the same section (the previous rune may be in the previous word)
seq = list(UNS); dbl = set(i for i in range(1, len(seq)) if seq[i]['c'] == seq[i - 1]['c'] and seq[i]['seg'] == seq[i - 1]['seg'])
idx = {id(r): i for i, r in enumerate(seq)}
words = list(uw.values())
D = where([[idx[id(r)] for r in w] for w in words], lambda w, i: w[i] in dbl)
U = where([[0] * len(w) for w in words], lambda w, i: True)
def summary(c, label):
    n = sum(c.values()); pos = collections.Counter()
    for (L, p), v in c.items(): pos['1-rune word' if L == 1 else p] += v
    print(f'{label:34s} n={n:5d} ' + '  '.join(f'{k} {pos[k] / n:.3f}' for k in ('initial', 'medial', 'final', '1-rune word')))
summary(E, 'EA in English (LP spelling)'); summary(D, 'unsolved doublets (2nd rune)'); summary(U, 'any rune of the unsolved text')
nE = sum(E.values()); nD = sum(D.values())
print('\nby word length (share of all):  length: EA-English / doublets / any-rune')
for L in range(1, 11):
    e = sum(v for (l, p), v in E.items() if l == L) / nE; dd = sum(v for (l, p), v in D.items() if l == L) / nD; u = sum(v for (l, p), v in U.items() if l == L) / sum(U.values())
    print(f'   {L:2d}: {e:.3f} / {dd:.3f} / {u:.3f}')
cons = sum(1 for i in dbl if i - 1 in dbl); print(f'\nconsecutive doublets (would be EA EA): {cons}')
print('doublets in 1-rune words:', sum(v for (l, p), v in D.items() if l == 1))
# chi-square of doublets' position classes vs EA-English and vs any-rune
classes = ['initial', 'medial', 'final', '1-rune word']
def vec(c):
    pos = collections.Counter()
    for (L, p), v in c.items(): pos['1-rune word' if L == 1 else p] += v
    return np.array([pos[k] for k in classes], float)
dv = vec(D)
for lab, ref in (('EA-English', vec(E)), ('any rune', vec(U))):
    p = ref / ref.sum(); e = dv.sum() * p; m = e > 0
    chi = (((dv - e) ** 2 / np.where(m, e, 1))[m]).sum() + (np.inf if (dv[~m] > 0).any() else 0)
    print(f'doublet positions vs {lab:10s}: chi2 {chi:.1f} (3 df; 7.8 = p 0.05)   expected counts {np.round(e, 1)} observed {dv.astype(int)}')
# (a) the doublet marks the FIRST rune of the pair instead
D1 = where([[idx[id(r)] for r in w] for w in words], lambda w, i: w[i] + 1 in dbl)
print('\nif the doublet marks the first rune of the pair:', dict(zip(classes, vec(D1).astype(int))))
# (b) which plaintext rune's word-position profile matches the doublets best?
print('\nplaintext runes ranked by fit of their word-position profile to the doublets (chi2, 3 df):')
fits = []
for X in range(29):
    ref = vec(where(eng, lambda w, i, X=X: w[i] == X))
    if ref.sum() < 30: continue
    p = (ref + 0.5) / (ref + 0.5).sum(); e = dv.sum() * p; chi = ((dv - e) ** 2 / e).sum()
    fits.append((chi, LAT[X], ref.sum() / sum(len(w) for w in eng)))
for chi, x, f in sorted(fits)[:6]: print(f'   {x:3s} chi2 {chi:6.1f}  English freq {f:.4f}')
