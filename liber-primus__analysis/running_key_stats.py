"""Would an English running key (a book) show? Simulate c = p + k with p and k both English (from different
parts of the published translations) and measure what's visible: unigram IoC, repeats (doublets), and IoC of the
difference stream; compare with the unsolved text and with the noise level for 12,956 runes."""
import os, json, collections, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'progressive_key.py')).read().split('dp = [')[0])   # P: English runes (~2900)
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
IDX = {r: i for i, r in enumerate(GP)}
U = [IDX[t[1]] for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
def ioc(xs, k=29):
    c = collections.Counter(xs); n = len(xs); return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * k
def dbl(xs): return sum(a == b for a, b in zip(xs, xs[1:])) / (len(xs) - 1)
P = np.array(P); n = len(P)
sims = []
for off in range(300, n - 300, 97):            # key = same English text started far away (approximately independent)
    k = np.roll(P, off)
    c29 = (P + k) % 29
    # mod 28 over the 28 non-zero symbols (zero symbol passes through): map 1..28 -> 0..27
    nz = (P != 0) & (k != 0)
    c28 = ((P[nz] - 1 + k[nz] - 1) % 28)
    sims.append((ioc(c29.tolist()), dbl(c29.tolist()), ioc(c28.tolist(), 28)))
s = np.array(sims)
rnd = [ioc(list(np.random.default_rng(i).integers(0, 29, len(U)))) for i in range(200)]
print('English + English running key (mod 29): IoC %.3f ± %.3f, doublets %.2f%%' % (s[:, 0].mean(), s[:, 0].std(), 100 * s[:, 1].mean()))
print('English + English running key (mod 28 on non-zero symbols): IoC %.3f (random 1.000)' % s[:, 2].mean())
print('random runes, %d long: IoC %.3f ± %.4f  -> a running key would sit %.0f standard deviations above random'
      % (len(U), np.mean(rnd), np.std(rnd), (s[:, 0].mean() - np.mean(rnd)) / np.std(rnd)))
print('unsolved text: IoC %.4f; autokey-removed, zeros dropped, on 28 symbols: IoC %.4f' % (
    ioc(U), ioc([(b - a) % 29 - 1 for a, b in zip(U, U[1:]) if (b - a) % 29], 28)))
