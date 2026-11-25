"""Which rare rune could be a top-level skip (form A: passed through, and also produced by the rest of the cipher)?
Its ciphertext occurrences are a mixture: a share w are genuine plaintext and follow that rune's English word-position
profile; the rest follow the random-position profile of the unsolved layout. Position class = (index from word start,
index from word end), each capped at 3 (16 classes) - e.g. -TIAN puts IA second from the end.
For each candidate: maximum-likelihood w (0..1), likelihood-ratio vs w = 0, and the w its English frequency predicts
(n*f / count). English: Blake MHH in LP spelling + solved LP. Controls: the same fit for every other rune."""
import os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
exec(open(os.path.join(HERE, 'ea_positions.py')).read().split("# (a)")[0].replace("print(", "(lambda *a, **k: None)("))
def cls(L, i): return min(i, 3) * 4 + min(L - 1 - i, 3)
ntot = sum(len(w) for w in eng); FREQ = np.zeros(29); PROF = np.zeros((29, 16))
for w in eng:
    for i, x in enumerate(w): FREQ[x] += 1; PROF[x, cls(len(w), i)] += 1
FREQ /= ntot; PROF = (PROF + 0.2) / (PROF + 0.2).sum(1, keepdims=True)
seq = list(UNS); C = np.array([r['c'] for r in seq])
wl = collections.Counter(r['word'] for r in seq); prev = None; k = 0; CL = []
for r in seq:
    k = k + 1 if r['word'] == prev else 0; prev = r['word']; CL.append(cls(wl[r['word']], k))
CL = np.array(CL); RAND = np.bincount(CL, minlength=16) / len(CL); n = len(C)
ws = np.linspace(0, 1, 1001)
def fit(X):
    obs = np.bincount(CL[C == X], minlength=16)
    ll = np.array([(obs * np.log(w * PROF[X] + (1 - w) * RAND)).sum() for w in ws])
    i = ll.argmax(); lr = 2 * (ll[i] - ll[0])
    ci = ws[ll >= ll[i] - 1.92]; return ws[i], lr, (ci.min(), ci.max()), obs.sum()
print(f'{"rune":4s} {"Eng freq":>8s} {"count":>5s} {"w if it were the skip":>22s} {"fitted w":>8s} {"95% CI":>14s} {"LR vs 0":>8s}')
rows = []
for X in range(29):
    w, lr, ci, cnt = fit(X); pred = min(1, n * FREQ[X] / cnt); rows.append((LAT[X], FREQ[X], cnt, pred, w, ci, lr))
for name in ('IA', 'X', 'J', 'OE', 'AE', 'EO', 'EA'):
    r = [r for r in rows if r[0] == name][0]
    print(f'{r[0]:4s} {r[1]:8.4f} {r[2]:5d} {r[3]:22.3f} {r[4]:8.3f}   ({r[5][0]:.3f}-{r[5][1]:.3f}) {r[6]:8.2f}')
lrs = sorted(r[6] for r in rows)
print(f'\ncontrol: LR for all 29 runes (none is expected to be genuine): median {np.median(lrs):.2f}, max {max(lrs):.2f} '
      f'({[r[0] for r in rows if r[6] == max(lrs)][0]}); LR > 3.84 is nominal p < 0.05')
