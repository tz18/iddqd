"""'Do four unreasonable things each day' (An Instruction). Reading 'unreasonable' as 'irrational' and the
user's 2*pi*r/4 = pi*r/2: keys = digits of pi*r/2 for many r (decimal and base 29, with/without integer part),
r per page (page number, rune count; key restarts each page), and the four classic irrationals pi, e, sqrt2, phi
(summed digit-wise, cycled one per rune). Through the full model (history_hypotheses.evaluate, 160 settings),
IoC and structure score, each against a random digit stream of the same base; then best-of-all vs best-of-all
random replicates."""
import os, sys
import numpy as np
from math import isqrt
sys.set_int_max_str_digits(0)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.argv = ['x']
exec(open(os.path.join(HERE, 'history_hypotheses.py')).read().split("# ---------------- key sources ----------------")[0])
NDIG = 20200; U = 10 ** (NDIG + 30)
def arctan_inv(x):
    s = t = U // x; x2 = x * x; k = 3; sg = -1
    while t: t //= x2; s += sg * (t // k); sg = -sg; k += 2
    return s
PI = 4 * (4 * arctan_inv(5) - arctan_inv(239))
E = 0; t = U; k = 0
while t: E += t; k += 1; t //= k
SQ2 = isqrt(2 * U * U); PHI = (U + isqrt(5 * U * U)) // 2
def digits(v, base, count=20000, integer=True):
    whole, frac = divmod(v, U); out = []
    if integer:
        w = []; x = whole
        while x: x, r = divmod(x, base); w.append(r)
        out += w[::-1] or [0]
    while len(out) < count:
        frac *= base; dgt, frac = divmod(frac, U); out.append(int(dgt))
    return np.array(out[:count])
keys = {}
R = [1, 2, 4, 8, 13, 28, 29, 109, 503, 509, 761, 1031, 1033, 1229, 1259, 3301, 845145127, 1595277641]
for r in R:
    v = PI * r // 2
    for base in (10, 29):
        for integer in (True, False):
            keys[f'pi*{r}/2 base{base}{" +int" if integer else ""}'] = digits(v, base, integer=integer)
for base in (10, 29):
    D4 = [digits(c, base) for c in (PI, E, SQ2, PHI)]
    keys[f'four irrationals summed base{base}'] = sum(D4)
    keys[f'four irrationals cycled base{base}'] = np.ravel(np.column_stack(D4))[:20000]
rng = np.random.default_rng(2026)
print('%-34s %7s %7s | control IoC / struct' % ('key', 'IoC', 'struct'), flush=True)
res = []
for name, K in keys.items():
    bi, bs = evaluate(K); hi = int(K.max()) + 1
    ci, cs = evaluate(rng.integers(0, hi, len(K)))
    res.append((name, bi, bs, ci, cs)); print('%-34s %7.4f %7.2f | %7.4f / %5.2f' % (name, bi, bs, ci, cs), flush=True)
# per-page r: key restarts each page, r = page number or the page's rune count
PAGEd = PAGE[1:]
def page_key(rfun, base):
    K = np.zeros(len(D), int); cache = {}
    for pg in np.unique(PAGEd):
        idx = np.nonzero(PAGEd == pg)[0]
        r = rfun(pg)
        if r not in cache: cache[r] = digits(PI * r // 2, base, count=400)
        K[idx] = cache[r][:len(idx)]
    return K
def eval_positional(Kpos):
    s = D; nz = s != 0; sv, kv = s[nz], Kpos[nz]; bi = bs = -9
    for x in (((sv - 1) - kv) % 28, ((sv - 1) + kv) % 28, sv * INV[kv % 28 + 1] % 29 - 1, sv * (kv % 28 + 1) % 29 - 1):
        bi = max(bi, ioc28(x)); bs = max(bs, score(x, 28)[0])
    return bi, bs
runes_on = {pg: int((PAGE == pg).sum()) for pg in np.unique(PAGE)}
for nm, rf in (('page number', lambda pg: int(pg)), ('unsolved-folder page number', lambda pg: int(pg) - 15), ('runes on page', lambda pg: runes_on[pg])):
    for base in (10, 29):
        bi, bs = eval_positional(page_key(rf, base))
        ci, cs = eval_positional(rng.integers(0, base, len(D)))
        res.append((f'per page r = {nm} base{base}', bi, bs, ci, cs)); print('%-34s %7.4f %7.2f | %7.4f / %5.2f' % (f'per page r={nm} b{base}', bi, bs, ci, cs), flush=True)
best_i = max(r[1] for r in res); best_s = max(r[2] for r in res)
print('\n%d keys. best real: IoC %.4f, struct %.2f (%s);  per-key controls best: IoC %.4f, struct %.2f; English IoC ~1.7'
      % (len(res), best_i, best_s, max(res, key=lambda r: r[2])[0], max(r[3] for r in res), max(r[4] for r in res)))
