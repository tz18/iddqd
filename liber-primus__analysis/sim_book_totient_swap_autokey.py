"""Simulate: plaintext + book running key -> + totient stream -> swap F (0) with the least frequent rune -> ct autokey.
Check (1) the doublet rate it produces, (2) whether the depth-free scan in totient_mask.py would still expose the
book key (autokey removed, totient subtracted at the right offset, swap NOT undone)."""
import os, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'progressive_key.py')).read().split('dp = [')[0])   # P: English runes
P = np.array(P); n = len(P)
book = np.roll(P, 1234)                                   # stand-in book: same English, far-shifted
sieve = np.ones(100000, bool); sieve[:2] = False
for i in range(2, 317):
    if sieve[i]: sieve[i * i::i] = False
primes = np.nonzero(sieve)[0]
tot = (primes[:n] - 1) % 29
x = (P + book + tot) % 29
freq = np.bincount(x, minlength=29) / n
rare = int(np.argmin(np.where(np.arange(29) == 0, 9, freq)))
print('after totient: rune frequencies %.2f%%-%.2f%%; least frequent %s at %.2f%%' % (100 * freq.min(), 100 * freq.max(), LAT[rare], 100 * freq[rare]))
y = x.copy(); y[x == 0] = rare; y[x == rare] = 0          # swap F with the least frequent rune
c = np.zeros(n, int); prev = 0
for i in range(n): prev = (prev + y[i]) % 29; c[i] = prev
dbl = (c[1:] == c[:-1]).mean()
print('doublet rate produced: %.2f%%   (unsolved LP: 0.66%%, random: 3.45%%)' % (100 * dbl))
def ioc(v):
    cnt = np.bincount(v, minlength=29); m = len(v); return (cnt * (cnt - 1)).sum() / (m * (m - 1)) * 29
ds = np.concatenate([[c[0]], (c[1:] - c[:-1]) % 29])
print('ciphertext IoC %.3f;  autokey removed %.3f;  autokey removed - totient (swap not undone) %.3f;  plain+book %.3f'
      % (ioc(c), ioc(ds), ioc((ds - tot) % 29), ioc((P + book) % 29)))
