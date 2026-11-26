"""Search-adjusted significance for the within-word lag-5 excess, and the repeated-chunk words.
(1) Generous search: for lags 2-30, three pair types (inside one word, across word gaps, any pair) and two directions
(excess or deficit), take the largest |z| (doublet lag 1 excluded). Null: the same max over 1000 texts made by shuffling
the unsolved runes with word lengths kept and the doublet deficit kept (shuffle until lag-1 repeats are as rare).
(2) Words where the same lag k (any k >= 2) gives 3 or more matches: real count vs the same null (max over k)."""
import os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import UNS, GP, LAT
rng = np.random.default_rng(7)
C = np.array([r['c'] for r in UNS]); WID = np.array([r['word'] for r in UNS])
_, WID = np.unique(WID, return_inverse=True)
pe = ((np.bincount(C, minlength=29) / len(C)) ** 2).sum()
def no_doublet_shuffle():
    """shuffle, then repair doublets by swapping until the lag-1 repeat count matches the real one"""
    x = rng.permutation(C); target = int((C[1:] == C[:-1]).sum())
    for _ in range(50):
        bad = np.nonzero(x[1:] == x[:-1])[0] + 1
        if len(bad) <= target: break
        for b in bad[target:]:
            j = rng.integers(len(x)); x[b], x[j] = x[j], x[b]
    return x
def maxz(x):
    best = 0
    for lag in range(2, 31):
        eq = x[lag:] == x[:-lag]; inw = WID[lag:] == WID[:-lag]
        for m in (inw, ~inw, np.ones_like(inw)):
            n = m.sum()
            if n < 30: continue
            z = (eq[m].sum() - n * pe) / np.sqrt(n * pe * (1 - pe)); best = max(best, abs(z))
    return best
def chunk_words(x, kmin=3):
    hits = []
    starts = np.r_[0, np.nonzero(WID[1:] != WID[:-1])[0] + 1, len(x)]
    for a, b in zip(starts[:-1], starts[1:]):
        w = x[a:b]
        for lag in range(2, len(w)):
            m = int((w[lag:] == w[:-lag]).sum())
            if m >= kmin: hits.append((a, lag, m)); break
    return hits
real_inw5 = None
eq = C[5:] == C[:-5]; m = WID[5:] == WID[:-5]; real5 = (eq[m].sum() - m.sum() * pe) / np.sqrt(m.sum() * pe * (1 - pe))
real_max = maxz(C); rh = chunk_words(C)
nulls = [no_doublet_shuffle() for _ in range(1000)]
nm = np.array([maxz(x) for x in nulls]); nh = np.array([len(chunk_words(x)) for x in nulls])
print(f'(1) within-word lag 5: z {real5:.2f}. Largest |z| over the whole search in the real text: {real_max:.2f}')
print(f'    null (1000 shuffles keeping word lengths and the doublet deficit): max |z| mean {nm.mean():.2f}, 95th pct {np.percentile(nm, 95):.2f}, 99th {np.percentile(nm, 99):.2f}')
print(f'    search-adjusted p for z {real5:.2f}: {np.mean(nm >= real5):.3f}')
print(f'(2) words with >= 3 matches at a single lag (any lag >= 2): real {len(rh)}; null mean {nh.mean():.2f}, p(>= real) {np.mean(nh >= len(rh)):.3f}')
for a, lag, mm in rh:
    w = C[a:a + int((WID == WID[a]).sum())]
    print(f'    page {UNS[a]["page"]}: lag {lag}, {mm} matches, {"".join(GP[v] for v in w)}  {"-".join(LAT[v] for v in w)}')
