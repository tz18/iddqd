"""Hypothesis: the cipher maps each WORD (or clause) to another rune string of the same length and the same GP sum.
Fingerprint: English reuses a few words a lot, so for each word length a handful of sums dominate (THE, AND, OF...).
If sums survive encryption, the unsolved ciphertext word sums must show the same concentration.
Statistic per length L: collision rate sum_s p(s)^2 of word sums, and the share of words whose sum is one of the
5 most common sums for that length. Compared with: solved plaintext words, Blake's MHH spelled into runes letter
by letter (with GP values), and nulls where unsolved word lengths are refilled with random runes (doublets kept rare)."""
import os, sys, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, UNS, VAL, d
V = np.array(VAL)
def words(rs, f):
    ws = collections.OrderedDict()
    for r in rs: ws.setdefault(r['word'], []).append(f(r))
    return list(ws.values())
uns = words(UNS, lambda r: r['c'])
sol = words([r for r in R if d['segments'][r['seg']]['solved']], lambda r: r['p'])
L2I = {k: i for i, k in enumerate("F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA".split())}
def spell(w, digraphs):
    w = w.upper().replace('QU', 'CW').replace('K', 'C').replace('V', 'U').replace('Z', 'S').replace('Q', 'C')
    out, i = [], 0
    while i < len(w):
        for g in (('ING', 'NG', 'TH', 'EA', 'EO', 'OE', 'AE', 'IA', 'IO') if digraphs else ()):
            if w.startswith(g, i): out.append(L2I['NG' if g == 'ING' else 'IA' if g == 'IO' else g]); i += len(g); break
        else:
            out.append(L2I.get(w[i], None)); i += 1
    return [x for x in out if x is not None]
bl = re.findall(r'[A-Za-z]+', open(os.path.join(HERE, 'sources', 'blake_marriage_of_heaven_and_hell.txt')).read())
bl_d = [spell(w, True) for w in bl]; bl_n = [spell(w, False) for w in bl]
def stats(ws, Ls=(1, 2, 3, 4, 5)):
    out = []
    for L in Ls:
        s = [int(V[w].sum()) for w in ws if len(w) == L]
        c = np.array(sorted(collections.Counter(s).values(), reverse=True)); p = c / c.sum()
        out.append(((p ** 2).sum(), p[:5].sum(), len(s)))
    return out
rng = np.random.default_rng(3); allc = np.array([r['c'] for r in UNS])
def null():
    x = rng.permutation(allc); out, i = [], 0
    for w in uns: out.append(list(x[i:i + len(w)])); i += len(w)
    return out
nl = [stats(null()) for _ in range(200)]
print('collision rate of word sums by word length (top-5-sum share in brackets)')
print(f'{"":30s}' + ''.join(f'{"L=" + str(L):>18s}' for L in (1, 2, 3, 4, 5)))
for name, ws in (('Blake, LP spelling', bl_d), ('Blake, letter by letter', bl_n), ('LP solved plaintext', sol), ('LP UNSOLVED ciphertext', uns)):
    print(f'{name:30s}' + ''.join(f'{a:9.3f} ({b:.2f})' + ' ' * 0 for a, b, n in stats(ws)))
mu = np.mean([[a for a, b, n in s] for s in nl], 0); sd = np.std([[a for a, b, n in s] for s in nl], 0)
mb = np.mean([[b for a, b, n in s] for s in nl], 0)
print(f'{"random runes, same lengths":30s}' + ''.join(f'{m:9.3f} ({b:.2f})' for m, b in zip(mu, mb)))
z = [(a - m) / s for (a, b, n), m, s in zip(stats(uns), mu, sd)]
print('unsolved vs random, z by length:', ' '.join(f'{v:+.2f}' for v in z))
# global constraint: a sum-preserving cipher keeps the mean GP value per rune
pt = np.concatenate([w for w in sol]); ct = np.concatenate(uns)
print(f'\nmean GP per rune: solved pt {V[pt].mean():.1f}, Blake (letter by letter) {V[np.concatenate([w for w in bl_n if w])].mean():.1f}, '
      f'unsolved ct {V[ct].mean():.1f} (SE {V[ct].std() / np.sqrt(len(ct)):.2f}); uniform runes {V.mean():.1f}')
