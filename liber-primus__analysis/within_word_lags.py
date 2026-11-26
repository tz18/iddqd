"""'5-lets': are runes 5 apart inside the same word equal more often than chance? For lags 1-10: count same-rune pairs
(i, i+lag) inside one word, vs (a) the expected rate from rune frequencies (binomial z) and (b) a shuffle null
(unsolved runes permuted across the text, word lengths kept, 2000 draws). Also the same lag ACROSS words (pairs that
span a word gap) and per word length for lag 5. Reference: solved plaintext (English) and solved ciphertext."""
import os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import UNS, R, d
rng = np.random.default_rng(55)
def words_of(rs, f):
    ws = collections.OrderedDict()
    for r in rs: ws.setdefault(r['word'], []).append(f(r))
    return [np.array(w) for w in ws.values()]
def counts(words, lag):
    eq = n = 0
    for w in words:
        if len(w) > lag: eq += int((w[lag:] == w[:-lag]).sum()); n += len(w) - lag
    return eq, n
def across(words, lag):
    seq = np.concatenate(words); wid = np.concatenate([np.full(len(w), i) for i, w in enumerate(words)])
    m = wid[lag:] != wid[:-lag]; return int((seq[lag:] == seq[:-lag])[m].sum()), int(m.sum())
U = words_of(UNS, lambda r: r['c']); allc = np.concatenate(U); lens = [len(w) for w in U]
pe = ((np.bincount(allc, minlength=29) / len(allc)) ** 2).sum()
def shuffled():
    x = rng.permutation(allc); out, i = [], 0
    for L in lens: out.append(x[i:i + L]); i += L
    return out
nulls = [shuffled() for _ in range(2000)]
print(f'unsolved: {len(U)} words; expected same-rune rate from frequencies {pe:.4f}')
print(f'{"lag":>3s} {"within-word same":>18s} {"rate":>7s} {"binom z":>8s} {"shuffle p(>=)":>13s} | {"across-word rate":>16s} {"z":>6s}')
for lag in range(1, 11):
    eq, n = counts(U, lag); z = (eq - n * pe) / np.sqrt(n * pe * (1 - pe))
    nl = np.array([counts(x, lag)[0] for x in nulls]); p = np.mean(nl >= eq)
    ae, an = across(U, lag); za = (ae - an * pe) / np.sqrt(an * pe * (1 - pe))
    print(f'{lag:3d} {eq:8d} / {n:7d} {eq / n:7.4f} {z:+8.2f} {p:13.4f} | {ae / an:16.4f} {za:+6.2f}')
print('\nlag 5 by word length (unsolved):')
for L in range(6, 14):
    ws = [w for w in U if len(w) == L]
    if ws: eq, n = counts(ws, 5); print(f'   length {L:2d}: {len(ws):3d} words, {eq:3d}/{n:4d} same = {eq / n:.4f} (expected {pe:.4f}, z {(eq - n * pe) / np.sqrt(n * pe * (1 - pe)):+.2f})')
for lab, f in (('solved plaintext', lambda r: r['p']), ('solved ciphertext', lambda r: r['c'])):
    S = words_of([r for r in R if d['segments'][r['seg']]['solved']], f); a = np.concatenate(S); ps = ((np.bincount(a, minlength=29) / len(a)) ** 2).sum()
    print(f'\n{lab}: ' + ', '.join(f'lag{lag} {counts(S, lag)[0] / max(counts(S, lag)[1], 1):.4f}' for lag in range(1, 8)) + f'  (expected {ps:.4f})')
