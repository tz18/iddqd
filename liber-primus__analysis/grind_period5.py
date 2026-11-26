"""Per-word period-5 key, ground out without the key. If each word is encrypted with its own key that repeats every
5 runes, runes j and j+5 of a word share a key value, so for any per-word shift cipher:
   c = p + k or c = p - k :  p[j+5] - p[j] = c[j+5] - c[j]   (mod 29)
   c = k - p (Beaufort)   :  p[j+5] - p[j] = -(c[j+5] - c[j])
   any per-position table :  p[j+5] == p[j]  exactly when  c[j+5] == c[j]
For every unsolved word of 7+ runes, find dictionary words (Blake corpus + solved LP, LP spelling and letter by letter)
of the same rune length that satisfy all L-5 constraints. Real words vs fake words (unsolved runes shuffled into the same
word lengths, doublet rate kept): how many words get at least one match. Lists matches for the longest words."""
import os, sys, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
from lp_common import UNS, LAT, GP
src = open(os.path.join(HERE, 'sum_preserving.py')).read(); exec(src[src.index('L2I = {'):src.index('bl = re.findall')])
rng = np.random.default_rng(31)
text = open(os.path.join(HERE, 'sources', 'blake', '_ALL.txt')).read() + open(os.path.join(ROOT, 'liber-primus__translation', 'liber-primus__translation.txt')).read()
vocab = sorted(set(w.upper() for w in re.findall(r"[A-Za-z]+", text)))
DICT = collections.defaultdict(dict)                     # length -> {rune tuple: word}
for w in vocab:
    for dig in (True, False):
        s = tuple(spell(w, dig))
        if len(s) >= 7: DICT[len(s)].setdefault(s, w)
DA = {L: (np.array(list(d.keys())), list(d.values())) for L, d in DICT.items()}
print('dictionary entries by length:', {L: len(d) for L, d in sorted(DICT.items()) if L <= 14})
ws = collections.OrderedDict()
for r in UNS: ws.setdefault(r['word'], []).append(r['c'])
W = [np.array(w) for w in ws.values()]; lens = [len(w) for w in W]; allc = np.concatenate(W)
def matches(c):
    L = len(c)
    if L not in DA: return {}
    P, names = DA[L]; dc = (c[5:] - c[:-5]) % 29; dp = (P[:, 5:] - P[:, :-5]) % 29
    out = {'shift': np.nonzero((dp == dc).all(1))[0], 'beaufort': np.nonzero((dp == (-dc) % 29).all(1))[0],
           'pattern': np.nonzero(((P[:, 5:] == P[:, :-5]) == (c[5:] == c[:-5])).all(1))[0]}
    return {k: [names[i] for i in v] for k, v in out.items()}
def tally(words):
    t = collections.Counter()
    for c in words:
        if len(c) >= 7:
            m = matches(c)
            for k, v in m.items(): t[k] += len(v) > 0
    return t
def fake():
    x = rng.permutation(allc)
    for _ in range(30):
        bad = np.nonzero(x[1:] == x[:-1])[0] + 1
        if len(bad) <= 85: break
        for b in bad: j = rng.integers(len(x)); x[b], x[j] = x[j], x[b]
    out, i = [], 0
    for L in lens: out.append(x[i:i + L]); i += L
    return out
real = tally(W); nl = [tally(fake()) for _ in range(100)]
n7 = sum(1 for L in lens if L >= 7)
for k in ('shift', 'beaufort', 'pattern'):
    v = np.array([t[k] for t in nl]); print(f'{k:9s}: words (of {n7} with 7+ runes) with >= 1 dictionary match: real {real[k]}, fakes {v.mean():.1f} +/- {v.std():.1f}, z {(real[k] - v.mean()) / max(v.std(), 0.5):+.2f}, p(fake >= real) {np.mean(v >= real[k]):.2f}')
print('\nmatches for unsolved words of 9+ runes (shift / beaufort):')
for w in ws.values():
    if len(w) >= 9:
        m = matches(np.array(w))
        if m.get('shift') or m.get('beaufort'):
            print(f"   {''.join(GP[x] for x in w)} ({len(w)})  shift: {', '.join(m['shift'][:6])}  | beaufort: {', '.join(m['beaufort'][:6])}")
