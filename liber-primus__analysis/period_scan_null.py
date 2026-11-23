"""Null distribution of the search 'best (page pair, period 2-40) column IoC on the autokey-removed stream'.
Each replicate = the whole search on a text whose runes are shuffled within each page (doublet count kept).
Reports p-value and z-score of the real best, and of the real pages-69-70 period-13 value under the
pre-specified hypothesis (that one pair, that one period)."""
import os, json, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
page = {}
for p in d['pages']:
    rs = [IDX[t[1]] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
    if rs: page[p['page']] = rs
ks = sorted(page); PAIRS = [(a, b) for a, b in zip(ks, ks[1:]) if b == a + 1 and len(page[a] + page[b]) >= 150]
def colp(x, per):
    t = 0
    for j in range(per):
        c = np.bincount(x[j::per], minlength=29); k = c.sum(); t += (c * (c - 1)).sum() / (k * (k - 1)) * 29 if k > 1 else 0
    return t / per
def ds(s): s = np.array(s); return (s[1:] - s[:-1]) % 29
def best_search(pg):
    return max(colp(ds(pg[a] + pg[b]), q) for a, b in PAIRS for q in range(2, 41))
rng = random.Random(7)
def shuf(s):
    a = s[:]; t = sum(x == y for x, y in zip(s, s[1:]))
    for _ in range(3000):
        rng.shuffle(a)
        if sum(x == y for x, y in zip(a, a[1:])) == t: return a
    return a
real = best_search(page)
null = np.array([best_search({k: shuf(v) for k, v in page.items()}) for _ in range(200)])
p = (1 + np.sum(null >= real)) / (1 + len(null))
print(f'search over {len(PAIRS)} page pairs x periods 2-40 ({len(PAIRS) * 39} combinations)')
print(f'real best: {real:.3f}; null (200 reruns): mean {null.mean():.3f}, sd {null.std():.3f}; z = {(real - null.mean()) / null.std():.2f}; p = {p:.3f}')
# pre-specified hypothesis: pages 69-70 at period 13 only
x = ds(page[69] + page[70]); v = colp(x, 13)
single = np.array([colp(ds(shuf(page[69] + page[70])), 13) for _ in range(5000)])
print(f'pre-specified (pages 69-70, period 13): {v:.3f}; null mean {single.mean():.3f}, sd {single.std():.3f}; z = {(v - single.mean()) / single.std():.2f}; p = {(1 + np.sum(single >= v)) / (1 + len(single)):.4f}')
print(f'if only the page pair was searched (53 pairs, period 13 fixed): Bonferroni p ~ {min(1, len(PAIRS) * (1 + np.sum(single >= v)) / (1 + len(single))):.3f}')
