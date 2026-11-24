"""Score 'peeled' text by how non-random it is, not by how English it is.
If the ciphertext is nested layers, removing a correct outer layer gives the next layer's ciphertext, which
usually carries its own fingerprints. Battery (each as a z-score vs uniform random of the same length/alphabet):
  unigram chi2, bigram chi2, max column-IoC over periods 2-40, max |lag-k repeat-rate z| for k=1..50,
  doublet-rate z (either direction), count of repeated 5-grams, zlib compressibility.
Combined score = max over the battery, calibrated by applying the same peel with random keys.
Then: candidate keystreams from full_model_harness are rescored with this instead of IoC."""
import os, sys, zlib, math, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
def battery(x, m):
    x = np.asarray(x) % m; n = len(x); out = {}
    cnt = np.bincount(x, minlength=m); e = n / m
    out['unigram'] = ((cnt - e) ** 2 / e).sum(); out['unigram'] = (out['unigram'] - (m - 1)) / math.sqrt(2 * (m - 1))
    bg = np.bincount(x[:-1] * m + x[1:], minlength=m * m); eb = (n - 1) / (m * m)
    out['bigram'] = (((bg - eb) ** 2 / eb).sum() - (m * m - 1)) / math.sqrt(2 * (m * m - 1))
    best = -9
    for P in range(2, 41):
        v = 0
        for j in range(P):
            c = np.bincount(x[j::P], minlength=m); k = c.sum(); v += (c * (c - 1)).sum() / (k * (k - 1)) * m
        v /= P
        # sd of mean column IoC under uniform: ~ sqrt(2(m-1)/m^2)*m / (n/P) / sqrt(P) -> use chi2 relation
        sd = math.sqrt(2 * (m - 1)) / (n / P) / math.sqrt(P)
        best = max(best, (v - 1) / sd)
    out['periodic IoC'] = best
    zs = []
    for k in range(1, 51):
        eq = (x[:-k] == x[k:]).sum(); N = n - k; p = 1 / m
        zs.append((eq - N * p) / math.sqrt(N * p * (1 - p)))
    out['lag repeats'] = max(abs(z) for z in zs[1:]) if len(zs) > 1 else 0
    out['doublets'] = abs(zs[0])
    g = collections.Counter(tuple(x[i:i + 5]) for i in range(n - 4)); rep = sum(v - 1 for v in g.values() if v > 1)
    lam = (n - 4) ** 2 / 2 / m ** 5; out['5-gram repeats'] = (rep - lam) / math.sqrt(lam + 1e-9)
    raw = bytes(x.astype(np.uint8)); comp = len(zlib.compress(raw, 9))
    out['compressibility'] = comp      # compared against the null directly
    return out
KEYS = ['unigram', 'bigram', 'periodic IoC', 'lag repeats', 'doublets', '5-gram repeats', 'compressibility']
def combined(b, null_stats):
    """max standardized deviation vs the null battery (compressibility: smaller = more structure)"""
    zs = {}
    for k in KEYS:
        mu, sd = null_stats[k]
        zs[k] = ((mu - b[k]) if k == 'compressibility' else (b[k] - mu)) / (sd or 1)
    return max(zs.values()), max(zs, key=zs.get), zs
def null_battery(sample_fn, m, reps=60):
    vals = collections.defaultdict(list); maxes = []
    rows = [battery(sample_fn(), m) for _ in range(reps)]
    for r in rows:
        for k in KEYS: vals[k].append(r[k])
    stats = {k: (float(np.mean(v)), float(np.std(v))) for k, v in vals.items()}
    maxes = [combined(r, stats)[0] for r in rows]
    return stats, maxes
if __name__ == '__main__':
    sys.argv = [sys.argv[0]]
    src = open(os.path.join(HERE, 'full_model_harness.py')).read()
    exec(src.split("print('\\ncandidate keystreams")[0])      # C, undo machinery, candidates, self-test data
    def peel(c, K, op, skip, offset):
        s = (c[1:] - c[:-1]) % 29; nz = s != 0
        step = nz.astype(int) if skip else np.ones(len(s), int); idx = np.cumsum(step) - step
        k = K[(idx + offset) % len(K)]; sv, kv = s[nz], k[nz]
        if op == 'add28': x = ((sv - 1) - kv) % 28
        elif op == 'sub28': x = ((sv - 1) + kv) % 28
        elif op == 'mul29': x = sv * INV29[kv % 28 + 1] % 29 - 1
        else: x = sv * (kv % 28 + 1) % 29 - 1
        return x                                     # values 0..27 (28 symbols)
    rng = np.random.default_rng(11)
    # calibration: same peel with random keystreams
    stats, maxes = null_battery(lambda: peel(C, rng.integers(0, 10 ** 6, 20000), 'add28', True, 0), 28, reps=80)
    thr = np.percentile(maxes, 99)
    print('null (random keys): combined score median %.2f, 99th pct %.2f, max %.2f' % (np.median(maxes), thr, max(maxes)))
    # sensitivity: buried layer. English -> Vigenere period 7 (mod 28 on non-zero) -> mod-28 inner keyed by K -> autokey.
    x = (Pn + 1) % 29; vig = rng.integers(0, 28, 7); Kin = rng.integers(0, 28, 20000)
    cc = [0]; j = 0; jv = 0
    for xi in x:
        if xi == 0: s = 0
        else:
            y = 1 + ((xi - 1) + vig[jv % 7]) % 28; jv += 1          # inner Vigenere layer
            s = 1 + ((y - 1) + Kin[j]) % 28; j += 1                  # the keyed layer we peel
        cc.append((cc[-1] + s) % 29)
    cc = np.array(cc)
    simstats, simmax = null_battery(lambda: peel(cc, rng.integers(0, 10 ** 6, 20000), 'add28', True, 0), 28, reps=60)
    sc, which, _ = combined(battery(peel(cc, Kin, 'add28', True, 0), 28), simstats)
    print('sensitivity check (English under a period-7 Vigenere, under the peeled layer): correct key scores %.1f via %s; wrong keys 99th pct %.2f'
          % (sc, which, np.percentile(simmax, 99)))
    # rescore every candidate keystream
    res = []
    for name, K in cands.items():
        bestc = (-9, None)
        for op in ('add28', 'sub28', 'mul29', 'imul29'):
            for skip in (False, True):
                for o in range(0, 20):
                    sc, which, _ = combined(battery(peel(C, K, op, skip, o), 28), stats)
                    if sc > bestc[0]: bestc = (sc, (op, 'skip zeros' if skip else 'every rune', o, which))
        res.append((bestc[0], name, bestc[1]))
    res.sort(reverse=True)
    ntests = 4 * 2 * 20
    print('\ncandidates rescored by structure (best of %d settings each; a single random key exceeds %.2f 1%% of the time):' % (ntests, thr))
    for sc, name, cfg in res[:8]: print('   %6.2f  %-34s %s' % (sc, name, cfg))
    # best-of-ntests null for comparison
    bmax = [max(combined(battery(peel(C, rng.integers(0, 10 ** 6, 20000), 'add28', True, 0), 28), stats)[0] for _ in range(ntests // 8)) for _ in range(8)]
    print('   for comparison, best of %d random keys: %s' % (ntests // 8, [round(b, 2) for b in bmax]))
    # fair control: random keystreams through exactly the same 160 settings, best-of-160 each
    fair = []
    for r in range(12):
        K = rng.integers(0, 10 ** 6, 20000); b = -9
        for op in ('add28', 'sub28', 'mul29', 'imul29'):
            for skip in (False, True):
                for o in range(0, 20):
                    b = max(b, combined(battery(peel(C, K, op, skip, o), 28), stats)[0])
        fair.append(b)
    fair = np.array(fair)
    print('\nfair control: best-of-160 for 12 random keys: median %.2f, max %.2f' % (np.median(fair), fair.max()))
    print('candidates above the control maximum:', [(round(s, 2), n) for s, n, _ in res if s > fair.max()])
