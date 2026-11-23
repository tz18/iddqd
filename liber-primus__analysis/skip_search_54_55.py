"""Reproduce: unsolved-folder pages 54-55 (= pages 69-70 here), ciphertext autokey removed, period-13 key,
skips chosen to maximize IoC, all skips at the same rune (a subset of that rune's occurrences).
Skip = the key does not advance there and the position drops out of the columns.
Search: for each rune r (two variants: skip where the CIPHERTEXT rune is r, or where the DIFFERENCE value is r),
greedy add/remove of single occurrences while the mean period-13 column IoC increases.
Controls: same search on the same pages with runes shuffled (doublet count kept), and on every other page pair."""
import os, json, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
page = {}
for p in d['pages']:
    rs = [IDX[t[1]] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
    if rs: page[p['page']] = rs
P = 13
def col_ioc(x):
    tot = 0
    for j in range(P):
        c = np.bincount(x[j::P], minlength=29); k = c.sum()
        tot += (c * (c - 1)).sum() / (k * (k - 1)) * 29 if k > 1 else 0
    return tot / P
def search(c):
    c = np.array(c); dd = (c[1:] - c[:-1]) % 29; cc = c[1:]
    best = (col_ioc(dd), None, 0)
    for variant, ref in (('ct rune', cc), ('difference', dd)):
        for r in range(29):
            occ = np.nonzero(ref == r)[0]
            if len(occ) == 0: continue
            skip = np.zeros(len(dd), bool); cur = col_ioc(dd[~skip])
            improved = True
            while improved:
                improved = False; bestgain = (cur, None)
                for o in occ:
                    skip[o] = ~skip[o]; v = col_ioc(dd[~skip]); skip[o] = ~skip[o]
                    if v > bestgain[0] + 1e-12: bestgain = (v, o)
                if bestgain[1] is not None:
                    skip[bestgain[1]] = ~skip[bestgain[1]]; cur = bestgain[0]; improved = True
            if cur > best[0]: best = (cur, f'{variant} {r} ({GP[r]})', int(skip.sum()))
    return best
rng = random.Random(1)
def shuffle_keep_doublets(s):
    a = s[:]; target = sum(x == y for x, y in zip(s, s[1:]))
    for _ in range(1000):
        rng.shuffle(a)
        if sum(x == y for x, y in zip(a, a[1:])) == target: return a
    return a
real_seq = page[69] + page[70]
real = search(real_seq)
print(f'pages 69-70 (unsolved-folder 54-55), {len(real_seq)} runes: no skips {col_ioc((np.array(real_seq[1:]) - np.array(real_seq[:-1])) % 29):.3f}; '
      f'best with skips {real[0]:.3f} (skipping {real[2]} occurrences of {real[1]})')
null = [search(shuffle_keep_doublets(real_seq))[0] for _ in range(100)]
null = np.array(null)
print(f'same search on shuffled pages 69-70 (100 runs): median {np.median(null):.3f}, 95th pct {np.percentile(null, 95):.3f}, max {null.max():.3f}; '
      f'share >= real: {np.mean(null >= real[0]):.2f}')
pairs = []
ks = sorted(page)
for a, b in zip(ks, ks[1:]):
    if b != a + 1 or a == 69: continue
    s = page[a] + page[b]
    if len(s) < 150: continue
    pairs.append((search(s)[0], a, b))
pairs.sort(reverse=True)
vals = np.array([p[0] for p in pairs])
print(f'same search on the other {len(pairs)} page pairs: median {np.median(vals):.3f}, max {vals.max():.3f} (pages {pairs[0][1]}-{pairs[0][2]}); pairs >= real: {int((vals >= real[0]).sum())}')
# ---- no skips: is pages 69-70 at period 13 unusual, and is 13 special? ----
def dstream(s): s = np.array(s); return (s[1:] - s[:-1]) % 29
def colp(x, per):
    tot = 0
    for j in range(per):
        c = np.bincount(x[j::per], minlength=29); k = c.sum(); tot += (c * (c - 1)).sum() / (k * (k - 1)) * 29 if k > 1 else 0
    return tot / per
x = dstream(real_seq)
ns = np.array([colp(dstream(shuffle_keep_doublets(real_seq)), 13) for _ in range(2000)])
print(f'\nno skips: pages 69-70 at period 13 = {colp(x, 13):.3f}; shuffled (2000): median {np.median(ns):.3f}, 99th pct {np.percentile(ns, 99):.3f}; share >= real {np.mean(ns >= colp(x, 13)):.4f}')
allpairs = [(colp(dstream(page[a] + page[b]), 13), a, b) for a, b in zip(ks, ks[1:]) if b == a + 1 and len(page[a] + page[b]) >= 150]
allpairs.sort(reverse=True)
print('top page pairs at period 13 (no skips):', [(round(v, 3), f'{a}-{b}') for v, a, b in allpairs[:5]])
pers = sorted(((colp(x, q), q) for q in range(2, 41)), reverse=True)
print('pages 69-70, all periods 2-40 (no skips), top 6:', [(q, round(v, 3)) for v, q in pers[:6]])
# per page and per half
for nm, s in (('page 69 alone', page[69]), ('page 70 alone', page[70]), ('page 68 alone', page[68])):
    print(f'{nm}: {len(s)} runes, period-13 column IoC {colp(dstream(s), 13):.3f}')
# multiple-testing view: max over all page pairs and periods 2-40 in shuffled text
def best_pair_period(pg):
    return max(colp(dstream(pg[a] + pg[b]), q) for a, b in zip(ks, ks[1:]) if b == a + 1 and len(pg[a] + pg[b]) >= 150 for q in range(2, 41))
realbest = best_pair_period(page)
sh = []
for _ in range(20):
    pg2 = {k: shuffle_keep_doublets(v) for k, v in page.items()}
    sh.append(best_pair_period(pg2))
print(f'best (page pair, period) anywhere: real {realbest:.3f}; shuffled texts (20): median {np.median(sh):.3f}, max {max(sh):.3f}')
