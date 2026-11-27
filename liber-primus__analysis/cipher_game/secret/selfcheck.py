"""Measure the brief's targets 1-12 on a ciphertext.json, and (same code) on the unsolved pages for calibration.
Usage: python3 selfcheck.py [ciphertext.json]. Rates are given +/- one binomial standard error."""
import sys, os, json, collections, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
VAL = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]
rng = np.random.default_rng(3301)

def isprime(n): return n > 1 and all(n % q for q in range(2, int(n ** .5) + 1))
def se(k, n): p = k / n; return math.sqrt(p * (1 - p) / n)
def pct(k, n): return f'{100 * k / n:.2f}% +/- {100 * se(k, n):.2f} ({k}/{n})'

def load_unsolved():
    sys.path.insert(0, ROOT); from lp_common import UNS
    cl = collections.OrderedDict()
    for r in UNS: cl.setdefault(r['clause'], collections.OrderedDict()).setdefault(r['word'], []).append(r['c'])
    return [list(w.values()) for w in cl.values()]

def col_ioc(x, P):
    num = den = 0
    for j in range(P):
        col = x[j::P]; n = np.bincount(col, minlength=29); num += (n * (n - 1)).sum(); den += len(col) * (len(col) - 1)
    return 29 * num / den

def period_scan(x, nshuf=100):
    """max over P=1..100 of the column-IoC z (z from shuffles of the same stream), vs the same max on shuffles."""
    Ps = range(1, 101)
    sh = [rng.permutation(x) for _ in range(nshuf)]
    S = np.array([[col_ioc(s, P) for P in Ps] for s in sh]); mu, sd = S.mean(0), S.std(0)
    z = (np.array([col_ioc(x, P) for P in Ps]) - mu) / sd
    zmax_null = ((S - mu) / sd).max(1)
    b = int(np.argmax(z)); return z[b], b + 1, float(np.mean(zmax_null >= z[b]))

def measure(clauses):
    words = [w for cl in clauses for w in cl]; seq = np.array([r for w in words for r in w]); N = len(seq)
    wid = np.concatenate([np.full(len(w), i) for i, w in enumerate(words)])
    pos = np.concatenate([np.arange(len(w)) for w in words]); wl = np.concatenate([np.full(len(w), len(w)) for w in words])
    out = {}
    # 1 doublets
    dbl = seq[1:] == seq[:-1]; same = wid[1:] == wid[:-1]
    out['1'] = (f'overall {pct(dbl.sum(), N - 1)}; inside words {pct(dbl[same].sum(), same.sum())}; '
                f'across gaps {pct(dbl[~same].sum(), (~same).sum())}')
    # 2 doublet place (second rune of the pair) in its word: first / middle / last; random = all runes after the 1st
    def place(i):
        if pos[i] == 0: return 0
        return 2 if pos[i] == wl[i] - 1 else 1
    di = np.nonzero(dbl)[0] + 1; dp = np.bincount([place(i) for i in di], minlength=3)
    ap = np.bincount([place(i) for i in range(1, N)], minlength=3) / (N - 1)
    out['2'] = (f'doublets first/middle/last {dp[0]}/{dp[1]}/{dp[2]} = ' + ' '.join(f'{v / max(dp.sum(), 1):.2f}' for v in dp) +
                f'; random positions ' + ' '.join(f'{v:.2f}' for v in ap) +
                f'; chi2 {(((dp - dp.sum() * ap) ** 2) / (dp.sum() * ap)).sum():.1f} on 2 df')
    # 3 flat frequencies, mean GP
    cnt = np.bincount(seq, minlength=29); e = N / 29; chi = ((cnt - e) ** 2 / e).sum()
    g = np.array(VAL)[seq]
    out['3'] = f'chi2 {chi:.1f} on 28 df (p {chi2_sf(chi, 28):.2f}); mean GP {g.mean():.1f} +/- {g.std() / math.sqrt(N):.1f} (flat {np.mean(VAL):.1f})'
    # 4 F count
    out['4'] = f'F {pct(cnt[0], N)} (flat 3.45%)'
    # 5 word lengths
    L = np.array([len(w) for w in words]); sh = [np.mean(L == k) for k in range(1, 10)] + [np.mean(L >= 10)]
    out['5'] = ' '.join(f'{s:.3f}' for s in sh) + f', mean {L.mean():.2f}; 2-rune share +/- {se((L == 2).sum(), len(L)):.3f}'
    # 6 word-length order
    r1 = np.corrcoef(L[1:], L[:-1])[0, 1]; fin = np.array([len(cl[-1]) for cl in clauses if len(cl) > 1])
    out['6'] = f'lag-1 r {r1:+.3f} +/- {1 / math.sqrt(len(L)):.3f}; clause-final words {fin.mean():.2f} +/- {fin.std() / math.sqrt(len(fin)):.2f} runes (all words {L.mean():.2f})'
    # 7 same rune lag 5 inside words / across gaps
    pe = ((cnt / N) ** 2).sum(); s7 = []
    for lag in (1, 2, 3, 4, 5, 6, 7, 8):
        m = wid[lag:] == wid[:-lag]; eq = seq[lag:] == seq[:-lag]
        k, n = int(eq[m].sum()), int(m.sum()); z = (k - n * pe) / math.sqrt(n * pe * (1 - pe))
        if lag == 5:
            ka, na = int(eq[~m].sum()), int((~m).sum())
            out['7'] = f'lag 5 inside words {pct(k, n)} (z {z:+.1f}); across gaps {pct(ka, na)}; baseline {100 * pe:.2f}%'
        s7.append(f'{lag}:{z:+.1f}')
    out['7'] += '; inside-word z by lag ' + ' '.join(s7)
    # 8 short clauses with prime sum
    sums = [(sum(VAL[r] for w in cl for r in w), sum(len(w) for w in cl)) for cl in clauses]
    short = [s for s, n in sums if n <= 31]; kp = sum(isprime(s) for s in short)
    null = []
    for _ in range(300):
        x = rng.permutation(seq); i = 0; c = 0
        for s, n in sums:
            if n <= 31: c += isprime(int(np.array(VAL)[x[i:i + n]].sum()))
            i += n
        null.append(c)
    out['8'] = f'{kp} of {len(short)} short clauses prime ({100 * kp / max(len(short), 1):.0f}%); shuffle null {np.mean(null):.1f} +/- {np.std(null):.1f}'
    # 9 clause lengths
    cw = np.array([len(cl) for cl in clauses]); cr = np.array([sum(len(w) for w in cl) for cl in clauses])
    out['9'] = f'{len(clauses)} clauses; words/clause mean {cw.mean():.1f} median {np.median(cw):.0f} max {cw.max()}; one-word clauses {(cw == 1).sum()} ({100 * np.mean(cw == 1):.0f}%); runes/clause mean {cr.mean():.1f}'
    # 10 periodic key
    d = (seq[1:] - seq[:-1]) % 29
    z1, p1, q1 = period_scan(seq); z2, p2, q2 = period_scan(d)
    out['10'] = f'raw: best period {p1} z {z1:+.1f} (p of max-over-100 {q1:.2f}); autokey-removed: best period {p2} z {z2:+.1f} (p {q2:.2f})'
    # 11 pass-through: most over-represented rune in raw ct and in the autokey-removed stream (excluding d = 0, the doublets)
    zr = (cnt - e) / math.sqrt(e * (1 - 1 / 29)); b = int(np.argmax(zr))
    dc = np.bincount(d, minlength=29)[1:]; ed = dc.sum() / 28; zd = (dc - ed) / math.sqrt(ed * (1 - 1 / 28)); bd = int(np.argmax(zd)) + 1
    out['11'] = f'most frequent raw rune {b} z {zr[b]:+.1f} (max of 29: expect ~+2); in d (d != 0) rune {bd} z {zd[bd - 1]:+.1f}; d=0 share {100 * (d == 0).mean():.2f}%'
    # 12 exact repeats
    s = ''.join(chr(65 + r) for r in seq); best = 0; reps = 0
    for Lr in range(5, 30):
        seen = collections.Counter(s[i:i + Lr] for i in range(N - Lr + 1)); r = [k for k, v in seen.items() if v > 1]
        if not r: break
        best, reps = Lr, len(r)
    out['12'] = f'longest exact repeat {best} runes ({reps} such)' if best else 'no exact repeat of 5+ runes'
    return out

def chi2_sf(x, k):   # survival function of chi2, k even (regularized gamma series)
    m = x / 2; t = math.exp(-m); s = t
    for i in range(1, k // 2): t *= m / i; s += t
    return s

TARGETS = {'1': '0.66% overall; 0.63% inside words, 0.81% across gaps', '2': 'random: 27% first, 51% middle, 22% last',
           '3': 'chi2 26 on 28 df; mean GP 51.6', '4': '3.5%', '5': '.029 .155 .249 .177 .109 .088 .075 .054 .027 .038, mean 4.47',
           '6': 'lag-1 -0.015; clause-final 4.2', '7': 'inside 4.9% (z +3.7); across 3.46%', '8': '18 of 54 (33%), chance ~15%',
           '9': 'English-sentence-like; 2 one-word clauses of 168', '10': 'none for periods 1-100, raw or autokey-removed',
           '11': 'none detectable', '12': 'one 6-rune repeat in 12,956 runes'}
if __name__ == '__main__':
    cf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'round1', 'ciphertext.json')
    mine = measure(json.load(open(cf))['clauses'])
    try: uns = measure(load_unsolved())
    except Exception as ex: uns = None; print('(unsolved data not loaded:', ex, ')')
    for k in map(str, range(1, 13)):
        print(f'== target {k}\n   brief     : {TARGETS[k]}')
        if uns: print(f'   unsolved  : {uns[k]}')
        print(f'   round 1   : {mine[k]}')
