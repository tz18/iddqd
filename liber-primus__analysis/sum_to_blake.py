"""Reverse codebook (user): GP sum -> Blake word. For each unsolved ciphertext word take its GP sum and look up Blake
words with that sum (LP spelling and letter by letter; codebooks: Urizen only, and all of Blake).
(1) Coverage: share of unsolved words whose sum has a codebook word, vs null words of the same lengths made from the
unsolved runes shuffled. (2) Sequence: for consecutive covered words, share where SOME candidate pair occurs as an
adjacent word pair in the codebook text, vs the same null. (3) A sample decoding (most frequent word per sum)."""
import os, sys, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import UNS, VAL
src = open(os.path.join(HERE, 'sum_preserving.py')).read(); exec(src[src.index('L2I = {'):src.index('bl = re.findall')])
V = np.array(VAL)
uw = collections.OrderedDict()
for r in UNS: uw.setdefault(r['word'], []).append(r['c'])
W = list(uw.values()); lens = [len(w) for w in W]; allc = np.array([x for w in W for x in w]); rng = np.random.default_rng(5)
def sums_of(words): return [int(V[w].sum()) for w in words]
def null_sums():
    x = rng.permutation(allc); out, i = [], 0
    for L in lens: out.append(int(V[x[i:i + L]].sum())); i += L
    return out
for book in ('The_Book_of_Urizen', '_ALL'):
    toks = [w.upper() for w in re.findall(r"[A-Za-z]+", open(os.path.join(HERE, 'sources', 'blake', book + '.txt')).read())]
    for dig in (True, False):
        gp = {w: int(sum(VAL[x] for x in spell(w, dig))) for w in set(toks)}
        by = collections.defaultdict(collections.Counter)
        for w in toks: by[gp[w]][w] += 1
        bigr = set(zip([gp[w] for w in toks[:-1]], [gp[w] for w in toks[1:]]))
        def score(s):
            cov = np.mean([x in by for x in s])
            pairs = [(a, b) for a, b in zip(s[:-1], s[1:]) if a in by and b in by]
            return cov, np.mean([p in bigr for p in pairs]) if pairs else 0
        real = score(sums_of(W)); nl = np.array([score(null_sums()) for _ in range(200)])
        lab = f'{"Urizen" if "Urizen" in book else "all Blake"}, {"LP spelling" if dig else "letter by letter"}'
        print(f'{lab:32s} vocab {len(gp):6d} | coverage {real[0]:.3f} (null {nl[:, 0].mean():.3f} +/- {nl[:, 0].std():.3f}, z {(real[0] - nl[:, 0].mean()) / nl[:, 0].std():+.2f})'
              f' | Blake-pair rate {real[1]:.3f} (null {nl[:, 1].mean():.3f} +/- {nl[:, 1].std():.3f}, z {(real[1] - nl[:, 1].mean()) / nl[:, 1].std():+.2f})')
        if book == 'The_Book_of_Urizen' and dig:
            dec = [by[s].most_common(1)[0][0] if s in by else '·' for s in sums_of(W)[:80]]
            print('   first 80 unsolved words decoded (most frequent Urizen word per sum, · = none):\n   ' + ' '.join(dec))
