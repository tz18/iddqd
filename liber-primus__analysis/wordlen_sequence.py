"""Why don't neighbouring word lengths anti-correlate in the unsolved pages? Battery on word-length sequences:
(1) autocorrelation at lags 1-5; (2) mutual information between consecutive lengths (capped at 8), vs shuffled order;
(3) lag-1 per section; (4) pairs inside a clause vs pairs across a clause break; (5) mean length of the first, second,
middle and last word of clauses. References: solved LP plaintext; Blake MHH in LP spelling and letter by letter
(clauses split at . ; : ! ?). Null for the unsolved text: word order shuffled within clauses / globally."""
import os, sys, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, UNS, d
src = open(os.path.join(HERE, 'sum_preserving.py')).read(); exec(src[src.index('L2I = {'):src.index('def stats')])
rng = np.random.default_rng(17)
def clauses_lp(rs):
    out = collections.OrderedDict()
    for r in rs: out.setdefault(r['clause'], collections.OrderedDict()).setdefault(r['word'], 0); out[r['clause']][r['word']] += 1
    return [list(c.values()) for c in out.values()]
def clauses_blake(dig):
    txt = open(os.path.join(HERE, 'sources', 'blake_marriage_of_heaven_and_hell.txt')).read()
    out = []
    for s in re.split(r'[.;:!?]', txt):
        ws = [len(spell(w, dig)) for w in re.findall(r'[A-Za-z]+', s)]; ws = [x for x in ws if x]
        if ws: out.append(ws)
    return out
TEXTS = {'LP unsolved': clauses_lp(UNS), 'LP solved (pt)': clauses_lp([r for r in R if d['segments'][r['seg']]['solved']]),
         'Blake, LP spelling': clauses_blake(True), 'Blake, letter by letter': clauses_blake(False)}
def acf(x, k): x = np.asarray(x, float) - np.mean(x); return (x[k:] * x[:-k]).sum() / (x * x).sum()
def mi(x):
    x = np.minimum(np.asarray(x), 8); a, b = x[:-1], x[1:]; j = np.zeros((9, 9))
    np.add.at(j, (a, b), 1); j /= j.sum(); pa = j.sum(1); pb = j.sum(0); m = j > 0
    return (j[m] * np.log2(j[m] / np.outer(pa, pb)[m])).sum()
def inside_vs_across(cls):
    ins, acr = [], []
    for i, c in enumerate(cls):
        ins += list(zip(c[:-1], c[1:]))
        if i + 1 < len(cls): acr.append((c[-1], cls[i + 1][0]))
    def corr(p): p = np.array(p, float); return np.corrcoef(p[:, 0], p[:, 1])[0, 1]
    return corr(ins), corr(acr), len(ins), len(acr)
def positions(cls):
    first = [c[0] for c in cls if len(c) >= 3]; second = [c[1] for c in cls if len(c) >= 4]
    last = [c[-1] for c in cls if len(c) >= 3]; mid = [x for c in cls if len(c) >= 5 for x in c[2:-1]]
    return np.mean(first), np.mean(second), np.mean(mid), np.mean(last), len(first)
print(f'{"text":24s} {"words":>6s} {"lag1":>7s} {"lag2":>7s} {"lag3":>7s} {"lag4":>7s} {"lag5":>7s} {"MI bits":>8s} | inside clause / across break | len: 1st 2nd mid last (n clauses)')
for name, cls in TEXTS.items():
    seq = [x for c in cls for x in c]
    a = [acf(seq, k) for k in range(1, 6)]; ins, acr, ni, na = inside_vs_across(cls); f, s2, m, l, nc = positions(cls)
    print(f'{name:24s} {len(seq):6d} ' + ' '.join(f'{v:+7.3f}' for v in a) + f' {mi(seq):8.4f} | {ins:+.3f} ({ni}) / {acr:+.3f} ({na}) | {f:.2f} {s2:.2f} {m:.2f} {l:.2f} ({nc})')
# nulls for the unsolved text
cls = TEXTS['LP unsolved']; seq = [x for c in cls for x in c]
g_acf = []; g_mi = []
for _ in range(500):
    s = rng.permutation(seq); g_acf.append(acf(s, 1)); g_mi.append(mi(s))
print(f'\nunsolved, global shuffle null: lag1 {np.mean(g_acf):+.3f} +/- {np.std(g_acf):.3f}; MI {np.mean(g_mi):.4f} +/- {np.std(g_mi):.4f}')
print(f'unsolved real: lag1 {acf(seq, 1):+.3f} (z {(acf(seq, 1) - np.mean(g_acf)) / np.std(g_acf):+.2f}); MI z {(mi(seq) - np.mean(g_mi)) / np.std(g_mi):+.2f}')
pf = []
for _ in range(500):
    sh = [list(rng.permutation(c)) for c in cls]; pf.append(positions(sh)[:4])
pf = np.array(pf); f, s2, m, l, nc = positions(cls)
print('unsolved clause-position means vs within-clause shuffle: ' + ', '.join(f'{nm} {v:.2f} (null {pf[:, i].mean():.2f} +/- {pf[:, i].std():.2f}, z {(v - pf[:, i].mean()) / pf[:, i].std():+.1f})' for i, (nm, v) in enumerate(zip(('1st', '2nd', 'mid', 'last'), (f, s2, m, l)))))
print('\nlag-1 by unsolved section:')
for s in range(7, 16):
    c = clauses_lp([r for r in UNS if r['seg'] == s]); sq = [x for cc in c for x in cc]
    if len(sq) > 50: print(f'   segment {s:2d}: words {len(sq):4d}  lag1 {acf(sq, 1):+.3f}  (sd ~ {1 / np.sqrt(len(sq)):.3f})')
# does the rune-level cipher run continuously across word gaps? (doublet deficit inside words vs across gaps)
c = np.array([r['c'] for r in UNS]); w = np.array([r['word'] for r in UNS]); s = np.array([r['seg'] for r in UNS]); cl = np.array([r['clause'] for r in UNS])
same = s[1:] == s[:-1]; dbl = (c[1:] == c[:-1]) & same
for lab, m in (('inside a word', (w[1:] == w[:-1]) & same), ('across a word gap', (w[1:] != w[:-1]) & (cl[1:] == cl[:-1]) & same), ('across a clause break', (cl[1:] != cl[:-1]) & same)):
    print(f'doublets {lab:22s}: {dbl[m].sum():3d}/{m.sum():5d} = {dbl[m].sum() / m.sum():.4f}   (random 0.034)')
