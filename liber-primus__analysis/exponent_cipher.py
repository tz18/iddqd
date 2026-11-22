"""'e seeks d': exponentiation (Pohlig-Hellman/RSA-style) on rune indices mod 29.
p = c^d mod 29 with d = e^-1 mod 28 (phi(29) = 28). A fixed exponent only relabels runes,
so only exponents that change per rune or per word can turn flat text into English (IoC ~1.73)."""
import os, json, collections
from math import gcd
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
PR = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
def ioc(xs):
    c = collections.Counter(xs); n = len(xs); return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * 29
def inv28(e):
    e %= 28
    return pow(e, -1, 28) if gcd(e, 28) == 1 else None
def words_of(segs):
    out, cur = [], None
    for p in d['pages']:
        for l in p['lines']:
            if l['s'] not in segs: continue
            for t in l['t']:
                if t[0] in '-.': cur = None; continue
                if t[0] != 'r': continue
                if cur is None: cur = []; out.append(cur)
                cur.append(IDX[t[1]])
    return out
UW = words_of(range(7, 16)); U = [c for w in UW for c in w]
SW = words_of((0, 1, 2, 3, 4, 5, 6, 16, 17))
primes = []; n = 2
while len(primes) < len(U) + 5:
    if all(n % q for q in primes if q * q <= n): primes.append(n)
    n += 1
def dec(c, e, op):
    """op 'exp': p = c^(e^-1); 'mul': p = c * e^-1 (mod 29)"""
    if op == 'exp':
        dd = inv28(e)
        return pow(c, dd, 29) if dd is not None else c
    e %= 29
    return c * pow(e, -1, 29) % 29 if e else c
print('unsolved IoC %.3f (random 1.00, English ~1.73)' % ioc(U))
for op in ('exp', 'mul'):
    tests = {}
    tests['e = GP value of previous ct rune'] = [dec(U[i], PR[U[i - 1]] if i else 1, op) for i in range(len(U))]
    tests['e = previous ct index'] = [dec(U[i], U[i - 1] if i else 1, op) for i in range(len(U))]
    tests['e = i-th prime'] = [dec(U[i], primes[i], op) for i in range(len(U))]
    tests['e = GP sum of the word (numbers = direction)'] = [dec(c, sum(PR[x] for x in w), op) for w in UW for c in w]
    tests['e = GP sum of the previous word'] = [dec(c, sum(PR[x] for x in UW[k - 1]) if k else 1, op) for k, w in enumerate(UW) for c in w]
    ss = [sum(PR[x] for x in w) for w in SW]
    tests['e = k-th solved word sum (per word)'] = [dec(c, ss[k % len(ss)], op) for k, w in enumerate(UW) for c in w]
    tests['e = k-th solved word sum (per rune)'] = [dec(U[i], ss[i % len(ss)], op) for i in range(len(U))]
    tests['e = position in word + 1'] = [dec(c, j + 1, op) for w in UW for j, c in enumerate(w)]
    tests['e = word length'] = [dec(c, len(w), op) for w in UW for c in w]
    print(f'\n{"exponent" if op == "exp" else "multiplier"}  p = c^(1/e)' if op == 'exp' else '\nmultiplier  p = c / e (mod 29)')
    for name, xs in tests.items(): print(f'   {ioc(xs):.3f}  {name}')
