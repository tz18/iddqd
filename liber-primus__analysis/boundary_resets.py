"""Does a (home-made) cipher reset its state at section / page / paragraph / line starts?
(1) first rune after each boundary: uniform? (chi2, and how often it is F)
(2) step across the boundary c_first - c_last_prev: does it keep the doublet shortage (state carried over)
    or show ~3.4% repeats (state reset)?"""
import os, json, math, collections
from scipy.stats import chi2 as chi2dist, binom
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
seq = []   # (rune, seg, page, para, line-key)
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        if not 7 <= l['s'] <= 15: continue
        for t in l['t']:
            if t[0] == 'r': seq.append((IDX[t[1]], l['s'], p['page'], l['p'], (p['page'], li)))
for name, k in (('section', 1), ('page', 2), ('paragraph', 3), ('line', 4)):
    starts = [i for i in range(len(seq)) if i == 0 or seq[i][k] != seq[i - 1][k]]
    first = [seq[i][0] for i in starts]
    c = collections.Counter(first); n = len(first); e = n / 29
    chi = sum((c.get(v, 0) - e) ** 2 / e for v in range(29))
    cross = [(seq[i][0] - seq[i - 1][0]) % 29 for i in starts if i > 0]
    zeros = sum(x == 0 for x in cross)
    p_reset = binom.sf(zeros - 1, len(cross), 1 / 29) if zeros else 1.0      # chance of this many if state reset (3.45%)
    p_carry = binom.cdf(zeros, len(cross), 0.0066) if True else 1.0
    print(f'{name:9s} starts {n:4d} | first-rune chi2 {chi:5.1f} on 28 df (p={chi2dist.sf(chi, 28):.2f}), F first {c.get(0,0)} ({c.get(0,0)/n:.1%}) '
          f'| repeats across the boundary {zeros}/{len(cross)} = {zeros/max(1,len(cross)):.2%}  [carried-over 0.66%, reset 3.45%]')
    if name in ('page', 'line'):
        p_if_reset = binom.cdf(zeros, len(cross), 1 / 29); p_if_carry = binom.sf(zeros - 1, len(cross), 0.0066) if zeros else 1
        print(f'          P(<= {zeros} repeats | reset) = {p_if_reset:.3f};  P(>= {zeros} | carried over) = {p_if_carry:.3f}')
