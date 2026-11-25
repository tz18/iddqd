"""Full pass-through test (user's model). Some plaintext rune X passes through; in the stream it appears as value v
(v = X, or relabelled by a fixed map, so all 29x29 pairs are tried). Model A: the rest of the cipher also produces v
uniformly -> count(v) ~ n*(f_X + (1-f_X)/29), and v's word-position profile is the mixture of X's English profile
(weight f_X) and the random profile. Model B: the rest never produces v -> count(v) ~ n*f_X and v's profile is X's
English profile. A pair (v, X) survives if the count is within 2 sd AND the position profile fits (chi2, 3 df, p > 0.01).
Streams: raw ciphertext; autokey-removed (value at rune i = c[i]-c[i-1]). Whole unsolved text and each section.
English: Blake MHH in LP spelling + solved LP plaintext. Classes: word-initial, medial, final, 1-rune word."""
import os, sys, collections
import numpy as np
from scipy.stats import chi2 as CHI2
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
exec(open(os.path.join(HERE, 'ea_positions.py')).read().split("# (a)")[0].replace("print(", "(lambda *a, **k: None)("))
def cls(L, i): return 3 if L == 1 else 0 if i == 0 else 2 if i == L - 1 else 1
ntot = sum(len(w) for w in eng)
FREQ = np.zeros(29); PROF = np.zeros((29, 4))
for w in eng:
    for i, x in enumerate(w): FREQ[x] += 1; PROF[x, cls(len(w), i)] += 1
FREQ /= ntot; PROF = (PROF + 0.5) / (PROF + 0.5).sum(1, keepdims=True)
seq = list(UNS); C = np.array([r['c'] for r in seq]); SEG = np.array([r['seg'] for r in seq])
wl = collections.Counter(r['word'] for r in seq); pos_in = np.zeros(len(seq), int); prev = None; k = 0
for i, r in enumerate(seq):
    k = k + 1 if r['word'] == prev else 0; prev = r['word']; pos_in[i] = k
CLS = np.array([cls(wl[r['word']], pos_in[i]) for i, r in enumerate(seq)])
def run(stream, mask, label):
    vals = stream[mask]; cl = CLS[mask]; n = len(vals); rand = np.bincount(cl, minlength=4) / n
    surv = []
    for v in range(29):
        obs = np.bincount(cl[vals == v], minlength=4); cnt = obs.sum()
        for X in range(29):
            f = FREQ[X]
            for model in ('A', 'B'):
                e = n * (f + (1 - f) / 29) if model == 'A' else n * f
                if e < 5 or abs(cnt - e) > 2 * np.sqrt(e): continue
                prof = (n * f * PROF[X] + n * (1 - f) / 29 * rand) / e if model == 'A' else PROF[X]
                ex = cnt * prof; m = ex > 0.5
                chi = ((obs - ex) ** 2 / np.maximum(ex, 1e-9))[m].sum(); p = CHI2.sf(chi, m.sum() - 1)
                if p > 0.01: surv.append((model, LAT[v], LAT[X], f, cnt, round(e, 1), round(chi, 1), round(p, 3)))
    sA = [s for s in surv if s[0] == 'A']; sB = [s for s in surv if s[0] == 'B']
    print(f'\n== {label} ({n} values)')
    print(f'  model A survivors: {len(sA)}; passed rune X among them: {sorted(set(s[2] for s in sA))}')
    print(f'  model B survivors: {len(sB)}')
    for s in sorted(sB, key=lambda s: -s[7])[:12]: print('     B  value %-3s <- plaintext %-3s (Eng %.4f)  count %d vs %.1f  position chi2 %.1f p %.3f' % s[1:])
    return surv
diff = np.r_[-1, (C[1:] - C[:-1]) % 29]; okd = np.r_[False, SEG[1:] == SEG[:-1]]
run(C, np.ones(len(C), bool), 'raw ciphertext, all unsolved')
run(diff, okd, 'autokey-removed, all unsolved')
for s in range(7, 16):
    if (SEG == s).sum() < 500: continue
    run(C, SEG == s, f'raw ciphertext, segment {s}')
    run(diff, okd & (SEG == s), f'autokey-removed, segment {s}')
