"""Per-column period-13 IoC on pages 69-70 (unsolved-folder 54-55), autokey removed, and the odd/even split.
Column numbers given 1-based in two conventions: counted from the first difference, and counted from the first
rune of page 69 (difference i sits at rune i+1). Odd-vs-even contrast tested against shuffles."""
import os, json, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
seq = [IDX[t[1]] for p in d['pages'] if p['page'] in (69, 70) for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
def cols(s):
    s = np.array(s); dd = (s[1:] - s[:-1]) % 29; out = []
    for j in range(13):
        c = np.bincount(dd[j::13], minlength=29); k = c.sum(); out.append((c * (c - 1)).sum() / (k * (k - 1)) * 29)
    return np.array(out)
real = cols(seq)
print('column  from-1st-difference  from-1st-rune   IoC')
for j in range(13):
    print(f'  {j+1:2d}           {"odd " if (j+1) % 2 else "even"}              {"odd " if (j+2) % 2 else "even"}        {real[j]:.2f}')
def contrast(v, conv):
    idx = np.arange(13) + (1 if conv == 'diff' else 2)
    odd = v[idx % 2 == 1].mean(); even = v[idx % 2 == 0].mean(); return odd - even
rng = random.Random(3)
def shuf(s):
    a = s[:]; t = sum(x == y for x, y in zip(s, s[1:]))
    for _ in range(3000):
        rng.shuffle(a)
        if sum(x == y for x, y in zip(a, a[1:])) == t: return a
    return a
nulls = [cols(shuf(seq)) for _ in range(3000)]
for conv, name in (('diff', 'counted from 1st difference'), ('rune', 'counted from 1st rune')):
    r = contrast(real, conv); n = np.array([contrast(v, conv) for v in nulls])
    print(f'{name}: odd-minus-even mean IoC = {r:+.3f}; null sd {n.std():.3f}; z = {(r - n.mean()) / n.std():+.2f}; '
          f'p(one-sided, odd > even) = {(1 + np.sum(n >= r)) / (1 + len(n)):.3f}')
