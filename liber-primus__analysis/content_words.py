"""Codebook / word-salad hypothesis (the Some Wisdom square: SHADOWS AETHEREAL BUFFERS VOID ... are code words whose
GP sums fill a 1033 magic square). A plaintext of chosen code words has no grammar and no function words. Compare the
unsolved word-length distribution and lag-1 correlation with English (Blake, all 276k words) with function words
removed, in LP spelling and letter by letter. Also English with order shuffled (no grammar, function words kept)."""
import os, sys, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import UNS
src = open(os.path.join(HERE, 'sum_preserving.py')).read(); exec(src[src.index('L2I = {'):src.index('bl = re.findall')])
STOP = set('''a an the of to in on at by for from with into onto upon over under and or but nor so yet if then than as that this these those
which who whom whose what when where while why how is are was were be been being am do does did done have has had having will would shall should
can could may might must not no it its it's he him his she her hers they them their theirs we us our ours i me my mine you your yours thee thou
thy thine ye o oh all each every some any such own same other there here up out off down again also too very just only now'''.split())
words = [w.upper() for w in re.findall(r"[A-Za-z]+", open(os.path.join(HERE, 'sources', 'blake', '_ALL.txt')).read())]
def dist(L):
    L = np.array([l for l in L if l > 0]); s = np.array([np.mean(np.minimum(L, 10) == k) for k in range(1, 11)]); x = L - L.mean()
    return s, (x[1:] * x[:-1]).sum() / (x * x).sum(), L.mean(), len(L)
c = collections.Counter(r['word'] for r in UNS); U = [c[k] for k in sorted(c)]
rows = {'LP unsolved': U}
for dig, lab in ((True, 'LP spelling'), (False, 'letter by letter')):
    rows[f'Blake, all words, {lab}'] = [len(spell(w, dig)) for w in words]
    rows[f'Blake, content words only, {lab}'] = [len(spell(w, dig)) for w in words if w.lower() not in STOP]
us, ulag, um, un = dist(U)
print(f'{"":42s}' + ''.join(f'{k:>6d}' for k in range(1, 10)) + '   10+   mean  lag1   chi2 vs unsolved')
for name, L in rows.items():
    s, lag, m, n = dist(L)
    e = s * un; chi = ((us * un - e) ** 2 / np.maximum(e, 1e-9)).sum()
    print(f'{name:42s}' + ''.join(f'{v:6.3f}' for v in s) + f'  {m:5.2f} {lag:+.3f}   {chi:7.1f}' + ('' if name != 'LP unsolved' else '   (9 df)'))
