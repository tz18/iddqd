"""Where do doublets fall in the unsolved stream? Tests position modulo m (block sizes),
gaps between doublets, and position within line / page / word."""
import os, json, collections, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
stream = []   # (rune index, seg, page, line, pos-in-line, pos-in-word, word-start-flag)
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        if not 7 <= l['s'] <= 15: continue
        k = 0; inword = 0
        for t in l['t']:
            if t[0] in '-.': inword = 0; continue
            if t[0] != 'r': continue
            stream.append((IDX[t[1]], l['s'], p['page'], li, k, inword)); k += 1; inword += 1
N = len(stream)
dbl = [i for i in range(1, N) if stream[i][0] == stream[i - 1][0]]
print('unsolved runes', N, 'doublets', len(dbl))
def chi_uniform(vals, m):
    c = collections.Counter(v % m for v in vals); e = len(vals) / m
    return sum((c.get(r, 0) - e) ** 2 / e for r in range(m))
# 1) global position mod m, and position within segment mod m
segstart = {}
for i, s in enumerate(stream):
    segstart.setdefault(s[1], i)
res = []
for m in range(2, 61):
    for name, vals in (('global', dbl), ('in-segment', [i - segstart[stream[i][1]] for i in dbl])):
        x = chi_uniform(vals, m)
        z = (x - (m - 1)) / math.sqrt(2 * (m - 1))
        res.append((z, m, name, x))
res.sort(reverse=True)
print('top mod-m clustering (z of chi2; ~118 tests, so z>3.3 needed):', [(f'{n} m={m}', round(z, 2)) for z, m, n, x in res[:6]])
# 2) gaps between consecutive doublets vs geometric (memoryless)
gaps = [b - a for a, b in zip(dbl, dbl[1:])]
mean = sum(gaps) / len(gaps); sd = (sum((g - mean) ** 2 for g in gaps) / len(gaps)) ** .5
print('gaps: mean %.1f sd %.1f (geometric would have sd ~ mean)  min %d  short gaps<10: %d' % (mean, sd, min(gaps), sum(g < 10 for g in gaps)))
print('gaps divisible by small m:', {m: sum(g % m == 0 for g in gaps) for m in (2, 3, 4, 5, 6, 7, 8, 13, 29)}, 'of', len(gaps))
# 3) within line / word
first_in_line = sum(stream[i][4] == 0 for i in dbl)   # doublet straddles a line break
print('doublets straddling a line break: %d (expected %.1f)' % (first_in_line, len(dbl) * sum(s[4] == 0 for s in stream) / N))
print('doublets straddling a word gap: %d (expected %.1f)' % (sum(stream[i][5] == 0 for i in dbl), len(dbl) * sum(s[5] == 0 for s in stream[1:]) / (N - 1)))
print('which runes double:', collections.Counter(GP[stream[i][0]] for i in dbl).most_common())
print('doublets per segment:', {s: sum(stream[i][1] == s for i in dbl) for s in range(7, 16)}, 'runes per segment:', {s: sum(x[1] == s for x in stream) for s in range(7, 16)})
