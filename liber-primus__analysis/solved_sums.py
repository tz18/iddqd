"""'Book of primes': where are the primes? GP sums of words, clauses, lines, paragraphs, pages and sections in the
SOLVED segments, in plaintext (pt) and ciphertext (ct). For each unit, the share of prime sums vs a null that keeps
every unit's length but refills it with runes shuffled across the same text (2000 shuffles): z and p.
Also sums mod 29 == 0 and the product of GP values mod 29 / mod 3301."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, VAL, LAT, d
isprime = np.zeros(200000, bool)
from lp_common import PR
isprime[PR] = True
V = np.array(VAL)
S = [r for r in R if d['segments'][r['seg']]['solved'] and r.get('p') is not None]
rng = np.random.default_rng(1)
units = {'word': lambda r: r['word'], 'clause': lambda r: r['clause'], 'line': lambda r: (r['page'], r['line']),
         'paragraph': lambda r: (r['seg'], r['para']), 'page': lambda r: r['page'], 'section': lambda r: r['seg']}
for text in ('p', 'c'):
    x = np.array([r[text] for r in S])
    print(f'\n=== {"plaintext" if text == "p" else "ciphertext"} of solved segments ({len(x)} runes)')
    print(f'{"unit":10s} {"n":>5s} {"prime sums":>10s} {"null mean":>9s} {"z":>6s} {"p(>=)":>6s} | {"sum%29==0":>9s} {"null":>5s}')
    for u, key in units.items():
        g = np.array([hash(key(r)) for r in S]); starts = np.r_[0, np.nonzero(g[1:] != g[:-1])[0] + 1]
        def stats(y):
            s = np.add.reduceat(V[y], starts); return isprime[s].sum(), (s % 29 == 0).sum()
        rp, rz = stats(x); nul = np.array([stats(rng.permutation(x)) for _ in range(2000)])
        mu, sd = nul[:, 0].mean(), nul[:, 0].std() or 1
        print(f'{u:10s} {len(starts):5d} {rp:10d} {mu:9.1f} {(rp - mu) / sd:6.2f} {np.mean(nul[:, 0] >= rp):6.3f} | {rz:9d} {nul[:, 1].mean():5.1f}')
# notable: sections, pages whose pt or ct sum is prime
print('\nsection sums (pt / ct) and primality:')
for si in sorted(set(r['seg'] for r in S)):
    xs = [r for r in S if r['seg'] == si]; ps = sum(VAL[r['p']] for r in xs); cs = sum(VAL[r['c']] for r in xs)
    print(f'  {d["segments"][si]["name"]:28s} runes {len(xs):4d}  pt {ps:6d}{" prime" if isprime[ps] else "":6s}  ct {cs:6d}{" prime" if isprime[cs] else ""}')
