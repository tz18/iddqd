"""Is the unsolved text a linear filter (convolution, plain or recursive) of plaintext mod 29?
If c = h^-1 * p or c = h * p for a short kernel, some short kernel g applied to c gives p back:
p[i] = c[i] + g1 c[i-1] + g2 c[i-2] + g3 c[i-3] (mod 29). Try every g (leading 1; scaling only relabels)
and score IoC (English ~1.73, random 1.00). Compare the best score with the same search on shuffled text."""
import os, json, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
U = np.array([IDX[t[1]] for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r'])
def best_kernel(c):
    c0, c1, c2, c3 = c[3:], c[2:-1], c[1:-2], c[:-3]
    n = len(c0); best = (0, None)
    for g1 in range(29):
        for g2 in range(29):
            base = (c0 + g1 * c1 + g2 * c2) % 29
            # all g3 at once: shape (29, n)
            P = (base[None, :] + np.arange(29)[:, None] * c3[None, :]) % 29
            counts = np.stack([(P == v).sum(1) for v in range(29)], 1)
            ioc = (counts * (counts - 1)).sum(1) / (n * (n - 1)) * 29
            k = int(ioc.argmax())
            if ioc[k] > best[0]: best = (float(ioc[k]), (1, g1, g2, k))
    return best
real = best_kernel(U)
print('best kernel on the unsolved text: IoC %.3f  kernel %s' % real)
rng = np.random.default_rng(4)
nulls = [best_kernel(rng.permutation(U))[0] for _ in range(5)]
print('best kernel on shuffled text (5 runs):', [round(x, 3) for x in nulls])
# sanity check: build a fake ciphertext by convolving English with a kernel, then recover it
exec(open(os.path.join(HERE, 'progressive_key.py')).read().split('dp = [')[0])
Pn = np.array(P)
fake = Pn.copy()
for i in range(1, len(Pn)): fake[i] = (Pn[i] + 7 * fake[i - 1]) % 29   # recursive filter (autokey-like)
print('sanity check, English through a recursive filter: recovered IoC %.3f kernel %s' % best_kernel(fake))
