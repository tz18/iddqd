"""Fingerprints of non-classical sources of the doublet shortage:
(a) bytes -> runes by mod 29: 24 step values would occur 9/256 of the time and 5 values 8/256 (or other 2^k radices);
(b) human-made randomness: too few repeats at lag 2 (ABA), avoidance of alphabet-adjacent steps (+1/-1), too-even counts."""
import os, json, math, collections, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
segs = collections.OrderedDict()
for p in d['pages']:
    for l in p['lines']:
        if 7 <= l['s'] <= 15: segs.setdefault(l['s'], []).extend(IDX[t[1]] for t in l['t'] if t[0] == 'r')
D = [(b - a) % 29 for s in segs.values() for a, b in zip(s, s[1:])]
h = np.bincount(D, minlength=29); n = len(D)
nz = h[1:]; m = nz.mean()
print('step values (c[i]-c[i-1]) excluding 0: min %d max %d mean %.1f; chi2 vs flat %.1f on 27 df' % (nz.min(), nz.max(), m, ((nz - m) ** 2 / m).sum()))
# best split into a heavier group and a lighter group of fixed sizes, as byte encodings would produce
for radix in (32, 64, 128, 256):
    heavy = radix % 28 or 28           # values of the 28 non-zero steps that get one extra code point
    srt = np.sort(nz)[::-1]
    gap = srt[:heavy].mean() - srt[heavy:].mean() if heavy < 28 else 0
    expected_gap = m * (1 / (radix // 28 + (radix % 28 > 0)))
    print(f'  radix {radix:3d}: {heavy} step values should be heavier by ~{100 / (radix // 28):.0f}% ; observed best-case gap {gap:.1f} (vs mean {m:.0f})')
# lag-2 repeats (ABA) and alphabet-adjacent steps
S = [x for s in segs.values() for x in s]
pe = sum((c / len(S)) ** 2 for c in collections.Counter(S).values())
def rate(k): 
    eq = tot = 0
    for s in segs.values():
        for i in range(len(s) - k): tot += 1; eq += s[i] == s[i + k]
    return eq, tot
for k in (2, 3):
    eq, tot = rate(k); z = (eq - tot * pe) / math.sqrt(tot * pe * (1 - pe))
    print(f'repeat at distance {k}: {eq/tot:.4f} (expected {pe:.4f}, z={z:+.2f})')
adj = h[1] + h[28]; exp_adj = (n - h[0]) * 2 / 28
print('alphabet-adjacent steps (+1/-1): %d, expected %.0f (z=%+.2f)' % (adj, exp_adj, (adj - exp_adj) / math.sqrt(exp_adj)))
