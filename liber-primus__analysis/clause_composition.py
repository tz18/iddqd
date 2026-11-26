"""Were words moved within clauses or across them? Order-free test on clause COMPOSITION. For each text, compared with
the same text after shuffling words across clauses (clause sizes kept, 2000 draws):
 (1) spread of clause mean word length: mean of ((clause mean - overall mean) * sqrt(n) / sd)^2, ~1 if random
 (2) dispersion of short-word (<= 2 runes) counts per clause: mean of (count - n p)^2 / (n p (1-p)), ~1 if random
 (3) share of 8+-word clauses with no short word at all
 (4) correlation of mean word length between consecutive clauses (topic/style persistence, order across clauses)
English references: Blake split into sentences (. ! ?) and the solved LP plaintext; both spellings for Blake."""
import os, sys, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, UNS, d
src = open(os.path.join(HERE, 'sum_preserving.py')).read(); exec(src[src.index('L2I = {'):src.index('bl = re.findall')])
rng = np.random.default_rng(8)
def lp_clauses(rs):
    out = collections.OrderedDict()
    for r in rs: out.setdefault(r['clause'], collections.OrderedDict()).setdefault(r['word'], 0); out[r['clause']][r['word']] += 1
    return [list(c.values()) for c in out.values()]
blake = open(os.path.join(HERE, 'sources', 'blake', '_ALL.txt')).read()
def blake_clauses(dig, maxn=2000):
    out = []
    for s in re.split(r'[.!?]', blake):
        ws = [len(spell(w.upper(), dig)) for w in re.findall(r'[A-Za-z]+', s)]; ws = [x for x in ws if x]
        if 3 <= len(ws) <= 60: out.append(ws)
    return out[:maxn]
T = {'LP unsolved': [c for c in lp_clauses(UNS) if len(c) >= 3],
     'LP solved plaintext': [c for c in lp_clauses([r for r in R if d['segments'][r['seg']]['solved']]) if len(c) >= 3],
     'Blake sentences, LP spelling': blake_clauses(True), 'Blake sentences, letter by letter': blake_clauses(False)}
def stats(cls):
    m = np.array([np.mean(c) for c in cls]); n = np.array([len(c) for c in cls])
    allw = np.array([x for c in cls for x in c]); mu, sg = allw.mean(), allw.std(); p = np.mean(allw <= 2)
    short = np.array([sum(x <= 2 for x in c) for c in cls])
    big = [s for s, k in zip(short, n) if k >= 8]
    mm = m - m.mean(); lag = (mm[1:] * mm[:-1]).sum() / (mm * mm).sum()
    return np.mean(((m - mu) * np.sqrt(n) / sg) ** 2), np.mean((short - n * p) ** 2 / (n * p * (1 - p))), np.mean(np.array(big) == 0) if big else np.nan, lag
def shuffle(cls):
    pool = rng.permutation([x for c in cls for x in c]); out, i = [], 0
    for c in cls: out.append(list(pool[i:i + len(c)])); i += len(c)
    return out
print(f'{"text":36s} {"clauses":>7s} | {"mean-length spread":>20s} | {"short-word dispersion":>22s} | {"8+ clauses w/o short":>22s} | {"lag1 of clause means":>22s}')
for name, cls in T.items():
    r = stats(cls); nl = np.array([stats(shuffle(cls)) for _ in range(2000)])
    cells = []
    for k in range(4):
        mu, sd = np.nanmean(nl[:, k]), np.nanstd(nl[:, k])
        cells.append(f'{r[k]:6.3f} (z {(r[k] - mu) / sd:+5.1f})' if k < 3 else f'{r[k]:+6.3f} (z {(r[k] - mu) / sd:+5.1f})')
    print(f'{name:36s} {len(cls):7d} | {cells[0]:>20s} | {cells[1]:>22s} | {cells[2]:>22s} | {cells[3]:>22s}')
