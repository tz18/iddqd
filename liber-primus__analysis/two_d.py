"""1D or 2D? (1) repeat rate c[i]==c[i+k] for every lag k; (2) repeats between runes that are vertical or
diagonal neighbours on the printed page (using the workbench glyph boxes); (3) runes per line."""
import os, json, math, collections
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
segs = collections.OrderedDict()
for p in d['pages']:
    for l in p['lines']:
        if 7 <= l['s'] <= 15: segs.setdefault(l['s'], []).extend(t[1] for t in l['t'] if t[0] == 'r')
c = collections.Counter(r for s in segs.values() for r in s); n = sum(c.values())
pe = sum((v / n) ** 2 for v in c.values())
print('expected repeat rate for independent runes: %.4f' % pe)
rows = []
for k in range(1, 301):
    eq = tot = 0
    for s in segs.values():
        for i in range(len(s) - k): tot += 1; eq += s[i] == s[i + k]
    z = (eq - tot * pe) / math.sqrt(tot * pe * (1 - pe))
    rows.append((z, k, eq / tot))
print('lag 1: rate %.4f  z=%.1f' % (rows[0][2], rows[0][0]))
others = sorted(rows[1:], key=lambda r: r[0])
print('most extreme other lags (300 tested, |z|>3.4 needed):', [(k, round(rt, 4), round(z, 2)) for z, k, rt in others[:4]], [(k, round(rt, 4), round(z, 2)) for z, k, rt in others[-4:]])
# (2) page neighbours via glyph boxes
def neighbours():
    pairs = collections.Counter(); eqs = collections.Counter()
    for p in d['pages']:
        lines = [[t for t in l['t'] if t[0] == 'r' and len(t) == 6] for l in p['lines'] if 7 <= l['s'] <= 15]
        lines = [l for l in lines if l]
        for a, b in zip(lines, lines[1:]):           # line above, line below
            for g in b:
                gx0, gx1 = g[2], g[4]; cx = (gx0 + gx1) / 2
                # glyph above with the largest horizontal overlap, and its left/right neighbours
                ov = [(min(gx1, h[4]) - max(gx0, h[2]), j) for j, h in enumerate(a)]
                best = max(ov)
                if best[0] <= 0: continue
                j = best[1]
                for name, jj in (('directly above', j), ('above-left', j - 1), ('above-right', j + 1)):
                    if 0 <= jj < len(a):
                        pairs[name] += 1; eqs[name] += a[jj][1] == g[1]
    return pairs, eqs
pairs, eqs = neighbours()
for name in ('directly above', 'above-left', 'above-right'):
    tot, eq = pairs[name], eqs[name]
    z = (eq - tot * pe) / math.sqrt(tot * pe * (1 - pe))
    print(f'{name:15s}: same rune {eq}/{tot} = {eq/tot:.4f}  z={z:+.2f}')
# (3) runes per line
lens = [sum(1 for t in l['t'] if t[0] == 'r') for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15]
cl = collections.Counter(lens)
print('runes per line: min %d  max %d  mean %.1f  most common %s' % (min(lens), max(lens), sum(lens) / len(lens), cl.most_common(6)))
