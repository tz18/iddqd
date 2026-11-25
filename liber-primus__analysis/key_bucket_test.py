"""Cipher-agnostic key test. If each key rune selects SOME substitution alphabet (Vigenere, Beaufort, multiplication,
any keyed 29x29 table), the ciphertext runes that share a key rune went through one substitution, so their IoC is
the plaintext's (~1.7), whatever the table. Statistic: mean IoC within the 29 key-value buckets (weighted).
Calibration: solved Welcome (DIVINITY key, F-skips) and An End (totient) give the true key -> high; a shifted key -> ~1.
Candidates: prime-clause keys over the non-prime clauses, raw ciphertext and the autokey-removed stream,
with and without F-skip. Control: keys made of the same number of random non-prime clauses (200)."""
import os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, UNS, VAL, d, PR
exec(open(os.path.join(HERE, 'divine_keystream.py')).read().split("def ioc(x)")[0].split('"""', 2)[2])
def bucket_ioc(c, k, minn=30):
    tot = 0; w = 0
    for v in range(29):
        x = c[k == v]
        if len(x) < max(minn, 2): continue
        cnt = np.bincount(x, minlength=29); n = len(x); tot += (cnt * (cnt - 1)).sum() / (n * (n - 1)) * 29 * n; w += n
    return tot / w
def align(c, K, fskip):
    keep = (c != 0) if fskip else np.ones(len(c), bool); cc = c[keep]; kk = K[np.arange(len(cc)) % len(K)]
    return cc, kk
# calibration on solved sections
for si, name in ((1, 'Welcome'), (5, 'Koan 2'), (16, 'An End')):
    rs = [r for r in R if r['seg'] == si]; c = np.array([r['c'] for r in rs]); p = np.array([r['p'] for r in rs])
    k = (c - p) % 29                      # the true key actually applied (0 at skipped F)
    rk = [bucket_ioc(c, rng.integers(0, 29, len(c)), 2) for _ in range(200)]
    print(f'calibration {name:8s} ({len(c)} runes): true key {bucket_ioc(c, k, 2):.3f} | random keys {np.mean(rk):.3f} +/- {np.std(rk):.3f} | plaintext IoC {bucket_ioc(p, np.zeros_like(p), 2):.3f}')
D1 = lambda c: (c[1:] - c[:-1]) % 29
idx_np = np.nonzero(~prime)[0]
def score(K, stream, fskip):
    c = T if stream == 'raw' else D1(T)
    return bucket_ioc(*align(c, K, fskip))
for lab, mask in (('31 prime clauses', prime), ('18 short prime clauses', prime & short)):
    K = np.concatenate([c for c, m in zip(CL, mask) if m]); m = mask.sum()
    ctrl = []
    for _ in range(200):
        mm = np.zeros(len(CL), bool); mm[rng.choice(idx_np, m, replace=False)] = True
        ctrl.append(np.concatenate([c for c, x in zip(CL, mm) if x]))
    for stream in ('raw', 'autokey-removed'):
        for fs in (0, 1):
            for rev in (False, True):
                KK = K[::-1] if rev else K; real = score(KK, stream, fs); nl = np.array([score(k[::-1] if rev else k, stream, fs) for k in ctrl])
                print(f'{lab:24s} {stream:16s} fskip {fs} {"rev" if rev else "fwd"}: bucket IoC {real:.4f} | control {nl.mean():.4f} +/- {nl.std():.4f} z {(real - nl.mean()) / nl.std():5.2f}', flush=True)
for stream in ('raw', 'autokey-removed'):
    for fs in (0, 1):
        real = score(SOLP, stream, fs); nl = np.array([score(rng.integers(0, 29, len(SOLP)), stream, fs) for _ in range(200)])
        print(f'solved LP prime plaintext {stream:16s} fskip {fs}: bucket IoC {real:.4f} | control {nl.mean():.4f} +/- {nl.std():.4f} z {(real - nl.mean()) / nl.std():5.2f}')
