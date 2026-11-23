"""If c = p + k_book + phi(prime_i) (or with the autokey on top), subtracting the totient stream at the right
alignment exposes the book key's IoC (~1.05). Scan offsets 0..2999 into the prime sequence, three restart schemes
(whole unsolved text / each segment / each page), both signs, on the raw text and on the autokey-removed stream.
Noise level for ~13k runes: IoC sd ~0.0006, so anything near 1.05 would stand out by ~80 sd."""
import os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
rows = [(IDX[t[1]], l['s'], p['page']) for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
c = np.array([r[0] for r in rows]); seg = np.array([r[1] for r in rows]); page = np.array([r[2] for r in rows])
dstream = np.concatenate([[0], (c[1:] - c[:-1]) % 29])
def restart_index(groups):
    idx = np.zeros(len(groups), int)
    for i in range(1, len(groups)): idx[i] = 0 if groups[i] != groups[i - 1] else idx[i - 1] + 1
    return idx
schemes = {'whole text': np.arange(len(c)), 'each segment': restart_index(seg), 'each page': restart_index(page)}
N = 3000 + len(c) + 10
sieve = np.ones(200000, bool); sieve[:2] = False
for i in range(2, 448):
    if sieve[i]: sieve[i * i::i] = False
primes = np.nonzero(sieve)[0][:N]
streams = {'totient(primes)': (primes - 1) % 29, 'primes': primes % 29}
def ioc(x):
    cnt = np.bincount(x, minlength=29); n = len(x); return (cnt * (cnt - 1)).sum() / (n * (n - 1)) * 29
results = []
for sname, S in streams.items():
    for target_name, target in (('raw text', c), ('autokey removed', dstream)):
        for scheme, pos in schemes.items():
            for sign in (1, -1):
                best = (0, None)
                for off in range(3000):
                    v = ioc((target - sign * S[pos + off]) % 29)
                    if v > best[0]: best = (v, off)
                results.append((best[0], sname, target_name, scheme, sign, best[1]))
results.sort(reverse=True)
print('best IoC over 3000 offsets for each setting (book key would give ~1.05; noise max over 3000 offsets ~1.002):')
for r in results[:6]: print('   %.4f  %s  on %s, restart %s, sign %+d, offset %d' % r)
print('   ...lowest best: %.4f' % results[-1][0])
