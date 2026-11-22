"""Digraph (Playfair-like) test that tolerates skipped runes.
In a pair cipher, doublets fall only between pairs, so the number of *encrypted* runes between two
consecutive doublets is even. If rune X is passed through unencrypted (like F in the solved pages), count
only non-X runes. Try X = each rune and X = none; under the right X nearly all gaps would be even."""
import os, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
segs = {}
for p in d['pages']:
    for l in p['lines']:
        if 7 <= l['s'] <= 15: segs.setdefault(l['s'], []).extend(t[1] for t in l['t'] if t[0] == 'r')
rows = []
for X in [None] + list(GP):
    even = tot = 0; short_even = short_tot = 0
    for s in segs.values():
        r = [c for c in s if c != X]                 # encrypted runes only
        dbl = [i for i in range(1, len(r)) if r[i] == r[i - 1]]
        for a, b in zip(dbl, dbl[1:]):
            g = b - a; tot += 1; even += g % 2 == 0
            if g <= 60: short_tot += 1; short_even += g % 2 == 0
    z = (even - tot / 2) / math.sqrt(tot / 4)
    rows.append((z, X or 'none', even, tot, short_even, short_tot))
rows.sort(reverse=True)
print('skip rune | even gaps / all gaps | even / gaps <= 60 | z (all gaps)   [Playfair with the right skip: ~100% even]')
for z, X, e, t, se, st in rows[:6] + [r for r in rows if r[1] == 'none']:
    print(f'   {X:4s}  {e:3d}/{t:3d} = {e/t:.0%}   {se:3d}/{st:3d}   z={z:+.2f}')
print('lowest z:', round(rows[-1][0], 2), rows[-1][1])
