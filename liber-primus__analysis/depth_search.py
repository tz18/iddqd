"""Depth search on the autokey-removed stream.
d = c[i] - c[i-1] per page. If two pages share the inner key (any bijective combination: add, multiply, xor...),
then at the right alignment d_A[i] == d_B[i+o] whenever their inputs match -> coincidence rate ~6-7% instead of 1/29.
Slide every page against every other page (and the whole stream against itself) and look for outliers.
For the strongest alignments, also score the combined streams (sub, add, div, xor) by IoC."""
import os, json, math, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
pages = collections.OrderedDict()
for p in d['pages']:
    rs = [IDX[t[1]] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
    if len(rs) > 40: pages[p['page']] = np.array(rs)
D = {k: (v[1:] - v[:-1]) % 29 for k, v in pages.items()}
def onehot(x): return np.stack([(x == s).astype(float) for s in range(29)])
OH = {k: onehot(v) for k, v in D.items()}
# expected coincidence for independent streams: sum_v p_A(v) p_B(v) ~ 1/28 (zeros rare)
hits = []; ntests = 0
keys = list(D)
for a_i, a in enumerate(keys):
    for b in keys[a_i:]:
        A, B = OH[a], OH[b]
        la, lb = A.shape[1], B.shape[1]
        # match counts for offsets o in -(lb-1)..(la-1): A[i] vs B[i-o]
        m = sum(np.correlate(A[s], B[s], mode='full') for s in range(29))
        offs = np.arange(-(lb - 1), la)
        overlap = np.minimum(la, offs + lb) - np.maximum(0, offs)
        pa = A.mean(1); pb = B.mean(1); pe = float((pa * pb).sum())
        for o, mm, ov in zip(offs, m, overlap):
            if ov < 60 or (a == b and o <= 0): continue
            ntests += 1
            z = (mm - ov * pe) / math.sqrt(ov * pe * (1 - pe))
            hits.append((z, a, b, int(o), int(ov), int(round(mm))))
hits.sort(reverse=True)
zcut = math.sqrt(2) * 1.0 * 0  # placeholder
print(f'pages: {len(keys)}  page-pair/offset tests with >= 60 overlapping runes: {ntests}')
print('Bonferroni 5%% threshold: z > %.1f' % (abs(np.sqrt(2) * __import__("scipy.special", fromlist=["erfcinv"]).erfcinv(2 * 0.05 / ntests))))
print('top alignments (z, page A, page B, offset, overlap, matches):')
for h in hits[:10]: print('  ', tuple(round(x, 2) if isinstance(x, float) else x for x in h))
print('lowest z:', round(hits[-1][0], 2))
# combine streams at the top alignments
def ioc(xs):
    c = collections.Counter(xs.tolist()); n = len(xs)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * 29
inv = [0] + [pow(x, -1, 29) for x in range(1, 29)]
print('\ncombined streams at the top 5 alignments (IoC; random 1.00, English ~1.73, English differences ~1.13):')
for z, a, b, o, ov, mm in hits[:5]:
    A = D[a]; B = D[b]
    ia = np.arange(max(0, o), min(len(A), o + len(B))); ib = ia - o
    x, y = A[ia], B[ib]
    sub = (x - y) % 29; add = (x + y) % 29; div = (x * np.array([inv[v] for v in y])) % 29; xor = x ^ y
    print(f'   p{a} vs p{b} offset {o}: sub {ioc(sub):.3f}  add {ioc(add):.3f}  div {ioc(div):.3f}  xor {ioc(xor):.3f}')
# whole-stream self-alignment (all lags) via FFT
allD = np.concatenate([D[k] for k in keys]); n = len(allD)
tot = np.zeros(2 * n)
for s in range(29):
    f = np.fft.rfft((allD == s).astype(float), 2 * n)
    tot += np.fft.irfft(f * np.conj(f), 2 * n)
lags = np.arange(1, n - 100); counts = np.round(tot[1:n - 100]); ov = n - lags
pe = float(sum(((allD == s).mean()) ** 2 for s in range(29)))
zs = (counts - ov * pe) / np.sqrt(ov * pe * (1 - pe))
top = np.argsort(-zs)[:5]
print('\nwhole difference stream against itself, all %d lags: top z %s' % (len(lags), [(int(lags[i]), round(float(zs[i]), 2)) for i in top]))
