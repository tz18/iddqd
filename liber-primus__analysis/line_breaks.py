"""Line starts/ends where a word is split across the line break: which runes, and where."""
import os, json, collections
from scipy.stats import chi2 as chi2dist, binom
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
LAT = dict(zip(GP, ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]))
lines = [(p['page'], li, l['t']) for p in d['pages'] for li, l in enumerate(p['lines']) if 7 <= l['s'] <= 15]
allr = collections.Counter(t[1] for _, _, ts in lines for t in ts if t[0] == 'r'); N = sum(allr.values())
split_start, split_end, ea_pages = [], [], []
for (pa, la, ta), (pb, lb, tb) in zip(lines, lines[1:]):
    ra = [t for t in ta if t[0] in 'r-.']; rb = [t for t in tb if t[0] in 'r-.']
    if not ra or not rb: continue
    if ra[-1][0] == 'r' and rb[0][0] == 'r':        # no separator at the break: the word continues
        split_end.append(ra[-1][1]); split_start.append(rb[0][1])
        if rb[0][1] == 'ᛠ': ea_pages.append((pb, lb))
def show(name, rs):
    c = collections.Counter(rs); n = len(rs)
    chi = sum((c.get(v, 0) - n * allr[v] / N) ** 2 / (n * allr[v] / N) for v in GP)
    top = sorted(GP, key=lambda v: -(c.get(v, 0) - n * allr[v] / N) / (n * allr[v] / N) ** .5)
    print(f'{name:28s} n={n}  chi2 {chi:.1f} (p={chi2dist.sf(chi, 28):.2g})  most over: {[(LAT[v], c.get(v,0), round(n*allr[v]/N,1)) for v in top[:4]]}')
show('first rune after a split', split_start)
show('last rune before a split', split_end)
print('EA as first rune after a split: %d, expected %.1f, P(>=) = %.4f' % (split_start.count('ᛠ'), len(split_start) * allr['ᛠ'] / N,
      binom.sf(split_start.count('ᛠ') - 1, len(split_start), allr['ᛠ'] / N)))
print('pages of those EA line starts:', collections.Counter(p for p, _ in ea_pages).most_common())
# glyph width vs excess at line starts (widths learned by ../liber-primus__explorer/segment.py, as width/height)
import numpy as np
from scipy.stats import spearmanr
Wd = json.load(open(os.path.join(HERE, 'glyph_widths.json')))
cs = collections.Counter(split_start); ns = len(split_start)
zs = [(cs.get(v, 0) - ns * allr[v] / N) / (ns * allr[v] / N) ** .5 for v in GP]
print('glyph width vs excess at line starts after a split: Spearman rho = %.2f (p=%.2g)' % spearmanr([Wd[v] for v in GP], zs))
