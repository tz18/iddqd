"""Autokey outside, a layer that keeps 0 fixed inside:  c[i] = c[i-1] + s[i],  s[i] = L_i(p[i]) with L_i(0) = 0.
Candidates: s = p * k (k != 0) and s = p ** e.  Undo with d[i] = c[i] - c[i-1], then p = d / k or d ** (1/e)."""
import os, json, collections
from math import gcd
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
PR = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
def ioc(xs):
    c = collections.Counter(xs); n = len(xs); return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * 29
segs = {}
for p in d['pages']:
    for l in p['lines']:
        if 7 <= l['s'] <= 15:
            segs.setdefault(l['s'], []).extend(IDX[t[1]] for t in l['t'] if t[0] == 'r')
primes = []; n = 2
while len(primes) < 20000:
    if all(n % q for q in primes if q * q <= n): primes.append(n)
    n += 1
fib = [1, 1]
while len(fib) < 20000: fib.append((fib[-1] + fib[-2]) % 29)
def key_streams(L):
    ks = {
        'primes': [p % 29 for p in primes[:L]],
        'totient(primes)': [(p - 1) % 29 for p in primes[:L]],
        'fibonacci': fib[:L],
        'position+1': [(i + 1) % 29 for i in range(L)],
        'GP prime of position (cycling)': [PR[i % 29] % 29 for i in range(L)],
        'DIVINITY (+1)': [([23,10,1,10,9,10,16,26][i % 8] + 1) % 29 for i in range(L)],
        'FIRFUMFERENFE (+1)': [([0,10,4,0,1,19,0,18,4,18,9,0,18][i % 13] + 1) % 29 for i in range(L)],
    }
    return ks
best = []
for restart in ('per segment', 'whole stream'):
    groups = list(segs.values()) if restart == 'per segment' else [sum(segs.values(), [])]
    for kname in key_streams(10):
        for op in ('mul', 'exp'):
            for sgn in (1, -1):
                out = []
                for g in groups:
                    ks = key_streams(len(g))[kname]
                    for i in range(1, len(g)):
                        dd = (sgn * (g[i] - g[i - 1])) % 29
                        k = ks[i]
                        if op == 'mul':
                            out.append(dd * pow(k, -1, 29) % 29 if k % 29 else dd)
                        else:
                            e = PR[k % 29] if True else k
                            inv = pow(e % 28, -1, 28) if gcd(e % 28, 28) == 1 else None
                            out.append(pow(dd, inv, 29) if inv is not None else dd)
                best.append((ioc(out), restart, kname, op, sgn))
best.sort(reverse=True)
print('highest IoC (random 1.00, English ~1.73):')
for v, r, k, op, s in best[:6]: print(f'   {v:.3f}  {op}  key={k:28s} restart {r}  sign {s:+d}')
print('lowest:', round(best[-1][0], 3), ' n tests:', len(best))
