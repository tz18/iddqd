"""Do unsolved clause lengths look like English? LP '.' marks sentence ends (solved pages: commas stay inside a clause).
Compare words per clause and runes per clause with: solved LP plaintext; Blake MHH split at . ! ? (sentences) and at
. ! ? ; : (clauses), runes counted letter by letter and in LP spelling. Also a geometric null (breaks placed at random
word gaps with the same mean) and the lag-1 correlation of consecutive clause lengths."""
import os, sys, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, UNS, d
src = open(os.path.join(HERE, 'sum_preserving.py')).read(); exec(src[src.index('L2I = {'):src.index('def stats')])
def lp_clauses(rs):
    out = collections.OrderedDict()
    for r in rs: out.setdefault(r['clause'], collections.OrderedDict()).setdefault(r['word'], 0); out[r['clause']][r['word']] += 1
    return [list(c.values()) for c in out.values()]
blake = open(os.path.join(HERE, 'sources', 'blake_marriage_of_heaven_and_hell.txt')).read()
def blake_clauses(pat, dig):
    out = []
    for s in re.split(pat, blake):
        ws = [len(spell(w, dig)) for w in re.findall(r'[A-Za-z]+', s)]; ws = [x for x in ws if x]
        if ws: out.append(ws)
    return out
T = {'LP unsolved': lp_clauses(UNS),
     'LP solved plaintext': lp_clauses([r for r in R if d['segments'][r['seg']]['solved']]),
     'Blake sentences, letter by letter': blake_clauses(r'[.!?]', False),
     'Blake sentences, LP spelling': blake_clauses(r'[.!?]', True),
     'Blake clauses (. ! ? ; :), letter by letter': blake_clauses(r'[.!?;:]', False)}
def acf1(x): x = np.asarray(x, float) - np.mean(x); return (x[1:] * x[:-1]).sum() / (x * x).sum()
def desc(cls):
    w = np.array([len(c) for c in cls]); r = np.array([sum(c) for c in cls])
    q = np.percentile(w, [10, 25, 50, 75, 90])
    return w, r, q
print(f'{"text":44s} {"n":>4s} | words/clause: mean  sd    CV   p10 p25 med p75 p90  share<=3 | runes/clause mean  CV  | lag1(words)')
for name, cls in T.items():
    w, r, q = desc(cls)
    print(f'{name:44s} {len(w):4d} | {w.mean():5.1f} {w.std():5.1f} {w.std() / w.mean():4.2f}  ' + ' '.join(f'{v:3.0f}' for v in q) +
          f'  {np.mean(w <= 3):6.2f}   | {r.mean():6.1f} {r.std() / r.mean():4.2f} | {acf1(w):+.3f}')
w = np.array([len(c) for c in T['LP unsolved']]); rng = np.random.default_rng(1)
geo = [rng.geometric(1 / w.mean(), len(w)) for _ in range(2000)]
print(f'{"random break placement (geometric, same mean)":44s} {len(w):4d} | CV {np.mean([g.std() / g.mean() for g in geo]):.2f} +/- {np.std([g.std() / g.mean() for g in geo]):.2f}, '
      f'share<=3 {np.mean([np.mean(g <= 3) for g in geo]):.2f}')
# runes per word inside short vs long clauses (does the shuffle stay inside clauses?)
print('\nunsolved clause length in words, sorted list:', sorted(w.tolist()))
from scipy.stats import ks_2samp, geom
bl = np.array([len(c) for c in T['Blake sentences, letter by letter']])
print(f'\nKS test, unsolved vs Blake sentences (words/clause): D {ks_2samp(w, bl).statistic:.3f}, p {ks_2samp(w, bl).pvalue:.3f}')
g = rng.geometric(1 / w.mean(), 200000)
print(f'KS test, unsolved vs random break placement (geometric): D {ks_2samp(w, g).statistic:.3f}, p {ks_2samp(w, g).pvalue:.3f}')
print(f'clauses of 1 word: unsolved {np.sum(w == 1)}, geometric expects {len(w) * geom.pmf(1, 1 / w.mean()):.1f}, Blake-like expects {len(w) * np.mean(bl == 1):.1f}')
sd1 = np.std([acf1(rng.permutation(w)) for _ in range(2000)])
print(f'lag-1 of consecutive clause lengths: unsolved {acf1(w):+.3f} (shuffled sd {sd1:.3f}); Blake sentences {acf1(bl):+.3f}')
