"""Round 2 self-check. Part A: the brief's 12 targets on round2/ciphertext.json, each compared with 400 random contiguous,
clause-aligned blocks of the unsolved pages with the same number of words (block mean, block sd, z, percentile).
The statistics are those of round1/solver_scripts/compare.py (copied, plus the d-stream and period scans of
secret/selfcheck.py). Part B: the round-1 attack (difference stream, then divide by known multiplier streams) replayed.
Usage: python3 selfcheck.py > selfcheck_output.txt"""
import os, sys, json, math, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, ROOT)
from lp_common import UNS, R as LPR, PR
VAL = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]
rng = np.random.default_rng(3301)
def isprime(n): return n > 1 and all(n % p for p in range(2, int(n ** .5) + 1))
def flat(c): return [r for cl in c for w in cl for r in w]
def words(c): return [w for cl in c for w in cl]

def uns_clauses():
    cls = []; lc = lw = None
    for r in UNS:
        if r['clause'] != lc: cls.append([]); lc = r['clause']; lw = None
        if r['word'] != lw: cls[-1].append([]); lw = r['word']
        cls[-1][-1].append(r['c'])
    return cls

def col_ioc(x, P):
    num = den = 0
    for j in range(P):
        n = np.bincount(x[j::P], minlength=29); m = len(x[j::P]); num += (n * (n - 1)).sum(); den += m * (m - 1)
    return 29 * num / den

def period_z(x, Ps=range(1, 101), nshuf=60):
    sh = [rng.permutation(x) for _ in range(nshuf)]
    S = np.array([[col_ioc(s, P) for P in Ps] for s in sh]); mu, sd = S.mean(0), S.std(0)
    sd = np.where(sd > 0, sd, np.inf)
    z = (np.array([col_ioc(x, P) for P in Ps]) - mu) / sd; zn = ((S - mu) / sd).max(1)
    b = int(np.argmax(z)); return z[b], list(Ps)[b], float(np.mean(zn >= z[b]))

def stats(cls, full=False):
    S = {}; rs = np.array(flat(cls)); ws = words(cls); N = len(rs)
    inw = sum(sum(w[i] == w[i + 1] for i in range(len(w) - 1)) for w in ws); nin = sum(len(w) - 1 for w in ws)
    acr = sum(ws[i][-1] == ws[i + 1][0] for i in range(len(ws) - 1)); nac = len(ws) - 1
    S['1 dbl overall'] = (inw + acr) / (nin + nac); S['1 dbl inside'] = inw / nin; S['1 dbl gaps'] = acr / nac
    S['1 n doublets'] = inw + acr; S['1 share at gaps'] = acr / max(inw + acr, 1)
    pos = collections.Counter()
    for w in ws:
        for i in range(len(w) - 1):
            if w[i] == w[i + 1]: pos['first' if i == 0 else ('last' if i == len(w) - 2 else 'mid')] += 1
    t = sum(pos.values()) or 1
    for k in ('first', 'mid', 'last'): S['2 dbl place ' + k] = pos[k] / t
    cnt = np.bincount(rs, minlength=29); e = N / 29
    S['3 chi2 (28 df)'] = ((cnt - e) ** 2 / e).sum(); S['3 mean GP'] = np.mean([VAL[r] for r in rs])
    S['3 IoC'] = (cnt * (cnt - 1)).sum() / (N * (N - 1)) * 29
    S['4 F share'] = cnt[0] / N
    L = np.array([len(w) for w in ws])
    for k in range(1, 10): S[f'5 len {k}'] = (L == k).mean()
    S['5 len 10+'] = (L >= 10).mean(); S['5 mean length'] = L.mean()
    x = []; y = []
    for c in cls:
        l = [len(w) for w in c]; x += l[:-1]; y += l[1:]
    S['6 lag-1 r'] = np.corrcoef(x, y)[0, 1]
    S['6 clause-final len'] = np.mean([len(c[-1]) for c in cls if len(c) > 1])
    S['6 clause-first len'] = np.mean([len(c[0]) for c in cls if len(c) > 1])
    pe = ((cnt / N) ** 2).sum()
    for lag in (2, 3, 4, 5, 6):
        eq = n = 0
        for w in ws:
            for i in range(len(w) - lag): n += 1; eq += w[i] == w[i + lag]
        S[f'7 in-word lag {lag}'] = eq / max(n, 1)
    wid = np.concatenate([np.full(len(w), i) for i, w in enumerate(ws)]); m = wid[5:] != wid[:-5]
    S['7 lag 5 across gaps'] = (rs[5:] == rs[:-5])[m].mean(); S['7 baseline'] = pe
    sh = [c for c in cls if sum(len(w) for w in c) <= 31]
    S['8 short clauses'] = len(sh); S['8 short prime frac'] = sum(isprime(sum(VAL[r] for w in c for r in w)) for c in sh) / max(len(sh), 1)
    cw = np.array([len(c) for c in cls]); S['9 clauses'] = len(cls); S['9 words/clause mean'] = cw.mean()
    S['9 words/clause sd'] = cw.std(); S['9 one-word clauses'] = int((cw == 1).sum())
    d = (rs[1:] - rs[:-1]) % 29; nz = np.bincount(d, minlength=29)[1:]
    S['d IoC (28 nonzero)'] = (nz * (nz - 1)).sum() / (nz.sum() * (nz.sum() - 1)) * 28
    S['d chi2 nonzero (27 df)'] = ((nz - nz.sum() / 28) ** 2 / (nz.sum() / 28)).sum()
    s = ''.join(chr(65 + r) for r in rs); best = 0
    for k in range(4, 14):
        seen = set(); hit = False
        for i in range(N - k + 1):
            q = s[i:i + k]
            if q in seen: hit = True; break
            seen.add(q)
        if hit: best = k
        else: break
    S['12 longest repeat'] = best
    return S

C = json.load(open(os.path.join(HERE, '..', '..', 'round2', 'ciphertext.json')))['clauses']
U = uns_clauses(); SU = stats(U); SC = stats(C); nw = len(words(C))
blocks = []
for _ in range(400):
    st = rng.integers(len(U)); b = []; k = 0; i = st
    while k < nw: b.append(U[i % len(U)]); k += len(U[i % len(U)]); i += 1
    blocks.append(stats(b))
print(f'Round 2 ciphertext: {len(flat(C))} runes, {nw} words, {len(C)} clauses. Blocks: 400 unsolved blocks of ~{nw} words.\n')
print(f'{"statistic":26s} {"unsolved":>9s} {"blk mean":>9s} {"blk sd":>8s} {"round2":>9s} {"z":>6s} {"pctl":>5s}')
for k in SU:
    bv = np.array([b[k] for b in blocks], float); z = (SC[k] - bv.mean()) / (bv.std() + 1e-12)
    pc = (bv < SC[k]).mean() + 0.5 * (bv == SC[k]).mean()
    print(f'{k:26s} {SU[k]:9.4f} {bv.mean():9.4f} {bv.std():8.4f} {SC[k]:9.4f} {z:6.2f} {pc:5.3f}')
rs = np.array(flat(C)); nd = int(SC['1 n doublets'])
from scipy.stats import poisson, binomtest, chisquare
print(f'\nexact tests: doublets {nd} in {len(rs) - 1} pairs: Poisson p (two-sided vs 0.66%) = '
      f'{2 * min(poisson.cdf(nd, 0.0066 * (len(rs) - 1)), poisson.sf(nd - 1, 0.0066 * (len(rs) - 1))):.3f}; '
      f'vs flat 3.45%: p = {poisson.cdf(nd, 0.0345 * (len(rs) - 1)):.1e}')
ws = words(C); inw = sum(sum(w[i] == w[i + 1] for i in range(len(w) - 1)) for w in ws); nin = sum(len(w) - 1 for w in ws)
acr = nd - inw; nac = len(ws) - 1
from scipy.stats import fisher_exact
print(f'  inside vs across gaps: {inw}/{nin} vs {acr}/{nac}, Fisher p = {fisher_exact([[inw, nin - inw], [acr, nac - acr]])[1]:.2f}')
# doublet place vs random place (pairs at first / mid / last position, 2-rune words count as first)
exp = collections.Counter(); pos = collections.Counter()
for w in ws:
    for i in range(len(w) - 1):
        k = 'first' if i == 0 else ('last' if i == len(w) - 2 else 'mid'); exp[k] += 1; pos[k] += w[i] == w[i + 1]
ob = np.array([pos[k] for k in ('first', 'mid', 'last')]); ex = np.array([exp[k] for k in ('first', 'mid', 'last')], float)
print(f'  doublet place first/mid/last {ob.tolist()} vs random-position expectation {np.round(ex / ex.sum() * ob.sum(), 1).tolist()}: '
      f'chi2 p = {chisquare(ob, ex / ex.sum() * ob.sum()).pvalue:.2f}')
sh = [c for c in C if sum(len(w) for w in c) <= 31]; kp = sum(isprime(sum(VAL[r] for w in c for r in w)) for c in sh)
print(f'  short prime clauses {kp}/{len(sh)}: binomial p vs 33% = {binomtest(kp, len(sh), 18 / 54).pvalue:.2f}, vs 15% = {binomtest(kp, len(sh), 0.15).pvalue:.2f}')
L = np.array([len(w) for w in ws]); tgt = np.array([.029, .155, .249, .177, .109, .088, .075, .054, .027, .038])
ob = np.array([(L == k).sum() for k in range(1, 10)] + [(L >= 10).sum()]); ex = tgt / tgt.sum() * len(L)
print(f'  word lengths vs unsolved shape: chi2 {((ob - ex) ** 2 / ex).sum():.1f} on 9 df (LP digraph spelling; soft target)')
z1, p1, q1 = period_z(rs); d = (rs[1:] - rs[:-1]) % 29; z2, p2, q2 = period_z(d)
print(f'  period scan 1-100: raw best P={p1} z {z1:+.2f} (p of the max {q1:.2f}); autokey-removed best P={p2} z {z2:+.2f} (p {q2:.2f})')
from scipy.stats import binom
d2 = d[d != 0]; bestp = (1, 0)
for P in range(101, 2001):     # column coincidences (pairs in the same column), exact binomial against 1/28
    num = den = 0
    for j in range(P):
        n = np.bincount(d2[j::P], minlength=29); m = len(d2[j::P]); num += (n * (n - 1)).sum() // 2; den += m * (m - 1) // 2
    pv = binom.sf(num - 1, den, 1 / 28)
    if pv < bestp[0]: bestp = (pv, P)
print(f'  period scan 101-2000 on d (zeros dropped): smallest binomial p {bestp[0]:.4f} at P={bestp[1]}; '
      f'with 1,900 periods tried, Bonferroni p = {min(1, 1900 * bestp[0]):.2f}')
cnt = np.bincount(rs, minlength=29); e = len(rs) / 29; zr = (cnt - e) / math.sqrt(e); nz = np.bincount(d, minlength=29)[1:]
zd = (nz - nz.mean()) / math.sqrt(nz.mean())
print(f'  pass-through: max raw rune z {zr.max():+.1f}; max nonzero d value z {zd.max():+.1f} (max of 29/28 normals ~ +2)')

g = np.array(VAL)[rs]; fm = np.mean(VAL); fs = np.std(VAL) / math.sqrt(len(rs))
from scipy.stats import chi2 as CHI2
print(f'  target 3 with iid uncertainty (the overlapping-block sd above is too small for mean GP: ~5 independent blocks):')
print(f'    mean GP {g.mean():.2f} vs flat {fm:.2f} +/- {fs:.2f} (z {(g.mean() - fm) / fs:+.1f}); unsolved {SU["3 mean GP"]:.2f} '
      f'(z {(SU["3 mean GP"] - fm) / (np.std(VAL) / math.sqrt(len(UNS))):+.1f} on 12,956 runes); chi2 {SC["3 chi2 (28 df)"]:.1f}, p = {CHI2.sf(SC["3 chi2 (28 df)"], 28):.3f}')
import encrypt as E
Pt = E.to_runes(open(os.path.join(HERE, 'plaintext.txt')).read()); ch = []; mg = []
for off in range(1, 600, 10):
    rr = np.array(E.flat(E.encrypt(Pt, E.key_stream(off)))); cc = np.bincount(rr, minlength=29); ee = len(rr) / 29
    ch.append(((cc - ee) ** 2 / ee).sum()); mg.append(np.array(VAL)[rr].mean())
print(f'    same plaintext, 60 other book offsets (diagnostic only; offset 0 is the key): chi2 {np.mean(ch):.1f} +/- {np.std(ch):.1f}, '
      f'mean GP {np.mean(mg):.2f} +/- {np.std(mg):.2f} -> offset 0 (chi2 {SC["3 chi2 (28 df)"]:.1f}) is a ~2 sd fluctuation, not the mechanism')
for nm, S_ in (('unsolved', SU), ('round 2', SC)):
    print(f'  target 6 relative to own mean length: {nm}: clause-final minus mean {S_["6 clause-final len"] - S_["5 mean length"]:+.2f}, '
          f'clause-first minus mean {S_["6 clause-first len"] - S_["5 mean length"]:+.2f} (English: final ~+1.3 to +1.5, first ~-0.8)')
PL = json.load(open(os.path.join(HERE, 'plaintext_runes.json')))['clauses']; LP = np.array([len(w) for w in words(PL)])
xx = []; yy = []
for c in PL:
    l = [len(w) for w in c]; xx += l[:-1]; yy += l[1:]
print(f'  same statistics on the plaintext word breaks (before the length transposition): lag-1 r {np.corrcoef(xx, yy)[0, 1]:+.3f}, '
      f'clause-final {np.mean([len(c[-1]) for c in PL if len(c) > 1]):.2f}, first {np.mean([len(c[0]) for c in PL if len(c) > 1]):.2f}, mean {LP.mean():.2f}')
print(f'  word-length multiset per clause unchanged by the cipher: {all(sorted(map(len, a)) == sorted(map(len, b)) for a, b in zip(PL, C))}')
pf = flat(PL); print(f'  plaintext EA share {pf.count(28)}/{len(pf)} = {100 * pf.count(28) / len(pf):.2f}% (= the doublet rate by construction); '
      f'references in LP spelling: solved LP plaintext 0.67%, Blake MHH 0.88%, all Blake 0.86%')

# ---------------- Part B: the round-1 attack ----------------
print('\n=== Part B: the round-1 attack replayed on round 2 ===')
print('d = c_i - c_{i-1}; for each candidate stream k (offsets 0-3000; key index advancing on every rune, or only on d != 0;')
print('multiply by k or 1/k, or subtract k; zero stream values passed over), and IoC(p) on the nonzero d. English would give ~1.7.')
num = lambda r: (r + 1) % 29
cn = np.array([num(r) for r in rs]); dd = np.diff(np.concatenate([[0], cn])) % 29
INV = np.array([0] + [pow(v, 27, 29) for v in range(1, 29)])
def ioc29(v): n = np.bincount(v, minlength=29); return 29 * (n * (n - 1)).sum() / (len(v) * (len(v) - 1))
fib = [1, 1]
while len(fib) < 7000: fib.append((fib[-1] + fib[-2]) % 29)
book = [r['p'] for r in LPR if r.get('p') is not None]
gsum = np.cumsum([VAL[b] for b in book]) % 29
streams = {'primes': [p % 29 for p in PR[:7000]], 'totient p-1': [(p - 1) % 29 for p in PR[:7000]],
           'naturals': [i % 29 for i in range(1, 7001)], 'fibonacci': fib, 'squares': [i * i % 29 for i in range(1, 7001)],
           'triangular': [i * (i + 1) // 2 % 29 for i in range(1, 7001)], 'prime gaps': [(PR[i + 1] - PR[i]) % 29 for i in range(7000)],
           'LP solved pt (n=idx+1)': [(b + 1) % 29 for b in book], 'LP solved pt GP values': [VAL[b] % 29 for b in book],
           'LP solved pt GP running sum (TRUE KEY)': list(gsum)}
crng = np.random.default_rng(29)
for t in range(3): streams[f'CONTROL: random stream {t + 1}'] = list(crng.integers(1, 29, 7000))
nzmask = dd != 0
for name, s in streams.items():
    s = np.array([v for v in s if v % 29], int)
    best = (0, None)
    for mode in ('every rune', 'nonzero d only'):
        for inv in ('k^-1', 'k', '-k'):
            for off in range(0, min(3001, len(s) - len(dd))):
                if mode == 'every rune': k = s[off:off + len(dd)][nzmask]
                else: k = s[off:off + nzmask.sum()]
                if inv == '-k': v = ioc29((dd[nzmask] - k) % 29)
                else: v = ioc29((dd[nzmask] * (INV[k] if inv == 'k^-1' else k)) % 29)
                if v > best[0]: best = (v, (mode, inv, off))
    print(f'  {name:44s} best IoC {best[0]:.3f} at {best[1]}')
print('  (the CONTROL rows give the best-of-search level for a stream that has nothing to do with the cipher)')
