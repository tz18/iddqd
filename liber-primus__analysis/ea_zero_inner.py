"""Rotate so EA = 0, then look at the autokey-removed stream d = c[i] - c[i-1] (mod 29, within sections).
Model: zeros = plaintext EA passed through (0.66%); nonzero = inner encryption of the other 28 runes, which keeps 0.
Two inner-cipher domains, each made additive mod 28:  shift (x - 1) and multiplication (discrete log base 2 mod 29).
Periodic-key test: mean column IoC at period P = 1..100, key skipping EA positions or advancing on all, key continuous
across sections or restarting per section. Null: 40 streams with the same zero positions and random nonzero values;
the best z over everything is compared with the nulls' best z."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import UNS
C = np.array([r['c'] for r in UNS]); seg = np.array([r['seg'] for r in UNS])
same = seg[1:] == seg[:-1]; d = ((C[1:] - C[:-1]) % 29)[same]; sg = seg[1:][same]
LOG = np.zeros(29, int); x = 1
for e in range(28): LOG[x] = e; x = x * 2 % 29
print(f'stream: {len(d)} values, zeros (EA) {np.sum(d == 0)} = {np.mean(d == 0):.4f}')
def col_ioc_z(vals, pos, P):
    tot = n = 0
    for j in range(P):
        v = vals[pos % P == j]; c = np.bincount(v, minlength=28); k = len(v)
        if k > 1: tot += (c * (c - 1)).sum(); n += k * (k - 1)
    ioc = tot / n * 28
    # under uniform mod 28: E[ioc]=1, var ~ 2*27/28^2*28^2 / pairs -> sd of sum-of-pairs ratio
    sd = np.sqrt(2 * 27 / n) ; return ioc, (ioc - 1) / sd
def positions(skip, restart, zero):
    pos = np.zeros(len(d), int); cnt = 0; last = None
    for i in range(len(d)):
        if restart and sg[i] != last: cnt = 0; last = sg[i]
        pos[i] = cnt
        if not (skip and zero[i]): cnt += 1
    return pos
def scan(dd):
    zero = dd == 0; out = []
    for dom, f in (('shift', lambda v: v - 1), ('mult-log', lambda v: LOG[v])):
        for skip in (True, False):
            for restart in (False, True):
                pos = positions(skip, restart, zero)[~zero]; vals = f(dd[~zero])
                for P in range(1, 101):
                    ioc, z = col_ioc_z(vals, pos, P); out.append((z, ioc, dom, skip, restart, P))
    return out
real = scan(d); real.sort(reverse=True)
print('top real results (z, IoC x28, domain, key skips EA, restart per section, period):')
for r in real[:8]: print('   z %5.2f  IoC %.4f  %-8s skipEA=%-5s restart=%-5s P=%d' % r)
rng = np.random.default_rng(8); best = []
for _ in range(40):
    dd = d.copy(); nz = dd != 0; dd[nz] = rng.integers(1, 29, nz.sum()); best.append(max(scan(dd))[0])
best = np.array(best)
print(f'\nbest real z {real[0][0]:.2f} vs null best-of-scan {best.mean():.2f} +/- {best.std():.2f} (max {best.max():.2f}); p = {np.mean(best >= real[0][0]):.3f}')
for P in (13, 8, 28, 29):
    sel = [r for r in real if r[5] == P]; b = max(sel); print(f'   period {P:3d}: best z {b[0]:5.2f} ({b[2]}, skipEA={b[3]}, restart={b[4]})')
