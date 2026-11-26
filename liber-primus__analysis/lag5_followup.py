"""Follow-up on the within-word lag-5 excess: (1) by section and LP1/LP2; (2) by position of the pair inside the word
(0-5, 1-6, ...); (3) words with several lag-5 matches (repeated 5-rune patterns like ABCDEABCDE); (4) which runes repeat;
(5) English reference: within-word lag-5 repeat rate in Blake, LP spelling and letter by letter."""
import os, sys, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import UNS, LAT, GP
src = open(os.path.join(HERE, 'sum_preserving.py')).read(); exec(src[src.index('L2I = {'):src.index('bl = re.findall')])
ws = collections.OrderedDict()
for r in UNS: ws.setdefault(r['word'], []).append(r)
W = list(ws.values()); allc = np.array([r['c'] for r in UNS]); pe = ((np.bincount(allc, minlength=29) / len(allc)) ** 2).sum()
def z(eq, n): return (eq - n * pe) / np.sqrt(n * pe * (1 - pe))
print(f'expected rate {pe:.4f}\n(1) lag-5 within words by part:')
for lab, sel in [(f'segment {s}', (lambda s: lambda w: w[0]['seg'] == s)(s)) for s in range(7, 16)] + [('LP1 pages <=57', lambda w: w[0]['page'] <= 57), ('LP2 pages >=58', lambda w: w[0]['page'] >= 58)]:
    eq = n = 0
    for w in W:
        if sel(w) and len(w) > 5: c = np.array([r['c'] for r in w]); eq += int((c[5:] == c[:-5]).sum()); n += len(w) - 5
    if n: print(f'   {lab:16s} {eq:3d}/{n:4d} = {eq / n:.4f}  z {z(eq, n):+.2f}')
print('(2) by position of the pair in the word:')
pos = collections.Counter(); posn = collections.Counter()
for w in W:
    c = [r['c'] for r in w]
    for i in range(len(c) - 5): posn[i] += 1; pos[i] += c[i] == c[i + 5]
for i in sorted(posn):
    if posn[i] >= 30: print(f'   runes {i}-{i + 5}: {pos[i]:3d}/{posn[i]:4d} = {pos[i] / posn[i]:.4f}  z {z(pos[i], posn[i]):+.2f}')
print('(3) words with 2+ lag-5 matches:')
multi = []
for w in W:
    c = [r['c'] for r in w]; m = sum(c[i] == c[i + 5] for i in range(len(c) - 5))
    if m >= 2: multi.append((m, len(c), w[0]['page'], ''.join(GP[x] for x in c), '-'.join(LAT[x] for x in c)))
for row in sorted(multi, reverse=True): print('   %d matches, %2d runes, p%d  %s  %s' % row)
# expected number of words with >=2 matches under independence
from scipy.stats import binom
e2 = sum(binom.sf(1, len(w) - 5, pe) for w in W if len(w) > 6); print(f'   observed {len(multi)} words, expected {e2:.1f}')
print('(4) runes involved in lag-5 matches:')
cnt = collections.Counter()
for w in W:
    c = [r['c'] for r in w]
    for i in range(len(c) - 5):
        if c[i] == c[i + 5]: cnt[LAT[c[i]]] += 1
print('   ', cnt.most_common())
print('(5) English within-word lag-5 repeat rate (Blake):')
blake = open(os.path.join(HERE, 'sources', 'blake', '_ALL.txt')).read()
for dig in (True, False):
    eq = n = 0; allr = []
    for w in re.findall(r'[A-Za-z]+', blake):
        s = spell(w.upper(), dig); allr += s
        if len(s) > 5: eq += sum(s[i] == s[i + 5] for i in range(len(s) - 5)); n += len(s) - 5
    pb = ((np.bincount(allr, minlength=29) / len(allr)) ** 2).sum()
    print(f'   {"LP spelling" if dig else "letter by letter"}: {eq / n:.4f} (its own frequency expectation {pb:.4f}, ratio {eq / n / pb:.2f}); unsolved ratio {0.0494 / pe:.2f}')
# (6) raw ciphertext vs autokey-removed stream d = c[i]-c[i-1]: within-word repeat rates at lags 1-10
C = np.array([r['c'] for r in UNS]); SEG = np.array([r['seg'] for r in UNS]); WID = np.array([r['word'] for r in UNS])
D = np.r_[-1, (C[1:] - C[:-1]) % 29]; D[np.r_[True, SEG[1:] != SEG[:-1]]] = -1
pd_ = ((np.bincount(D[D >= 0], minlength=29) / (D >= 0).sum()) ** 2).sum()
print('(6) within-word same-value rate, raw vs autokey-removed (both members inside one word):')
for lag in range(1, 11):
    m = (WID[lag:] == WID[:-lag]); a = C[lag:][m] == C[:-lag][m]
    md = m & (D[lag:] >= 0) & (D[:-lag] >= 0); b = D[lag:][md] == D[:-lag][md]
    zb = (b.sum() - md.sum() * pd_) / np.sqrt(md.sum() * pd_ * (1 - pd_))
    print(f'   lag {lag:2d}: raw {a.mean():.4f} (z {z(a.sum(), m.sum()):+.2f}) | autokey-removed {b.mean():.4f} (z {zb:+.2f}, expected {pd_:.4f})')
# (7) does the 5-cycle restart at each word with a key SHARED by other words? Compare runes at in-word positions with the
# same index mod 5 in two DIFFERENT words: adjacent words, same clause, different clauses. Baseline: different index mod 5.
print('(7) same rune at matching in-word position (mod 5) in two different words:')
idx_in = []; prev = None; k = 0
for r in UNS:
    k = k + 1 if r['word'] == prev else 0; prev = r['word']; idx_in.append(k)
byw = collections.OrderedDict()
for r, j in zip(UNS, idx_in): byw.setdefault(r['word'], []).append((j, r['c'], r['clause']))
WL = list(byw.values()); rng2 = np.random.default_rng(1)
def rate(pairs):
    same = diff = ns = nd = 0
    for a, b in pairs:
        for ja, ca, _ in a:
            for jb, cb, _ in b:
                if ja % 5 == jb % 5: ns += 1; same += ca == cb
                else: nd += 1; diff += ca == cb
    return same, ns, diff, nd
adj = [(WL[i], WL[i + 1]) for i in range(len(WL) - 1) if WL[i][0][2] == WL[i + 1][0][2]]
clause = collections.defaultdict(list)
for w in WL: clause[w[0][2]].append(w)
same_cl = [(a, b) for ws in clause.values() for i, a in enumerate(ws) for b in ws[i + 2:]]
rand = [(WL[i], WL[j]) for i, j in rng2.integers(0, len(WL), (20000, 2)) if WL[i][0][2] != WL[j][0][2]]
for lab, pr in (('adjacent words, same clause', adj), ('same clause, not adjacent', same_cl), ('different clauses (random)', rand)):
    s, ns, df, nd = rate(pr)
    print(f'   {lab:28s} same index mod 5: {s / ns:.4f} (z {z(s, ns):+.2f}, n {ns}) | other indices: {df / nd:.4f} (z {z(df, nd):+.2f})')
