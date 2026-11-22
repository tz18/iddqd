"""Period-13 column IoC (autokey removed, zeros dropped) on pages 54-55, against
(a) every other pair of consecutive unsolved pages and (b) shuffles of the same runes."""
import os, json, collections, random
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
def ioc(xs):
    c = collections.Counter(xs); n = len(xs)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * 29 if n > 1 else 0
page = collections.OrderedDict()
for p in d['pages']:
    rs = [(l['s'], IDX[t[1]]) for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
    if rs: page[p['page']] = rs
def dstream(runes):
    dd = [(runes[i] - runes[i - 1]) % 29 for i in range(1, len(runes))]
    return [x for x in dd if x]
def col_ioc(xs, P):
    cols = [xs[j::P] for j in range(P)]
    return sum(ioc(c) for c in cols) / P
pg = list(page)
print('pages 54-55 segments:', sorted({s for k in (54, 55) for s, _ in page.get(k, [])}), ' runes:', sum(len(page.get(k, [])) for k in (54, 55)))
x = dstream([r for k in (54, 55) for _, r in page[k]])
print('period 13 column IoC on pages 54-55: %.3f' % col_ioc(x, 13))
ranks = sorted(((col_ioc(x, P), P) for P in range(1, 41)), reverse=True)
print('periods ranked on 54-55:', [(p, round(v, 3)) for v, p in ranks[:6]])
# (a) other consecutive pairs
pairs = []
for a, b in zip(pg, pg[1:]):
    if b != a + 1: continue
    y = dstream([r for k in (a, b) for _, r in page[k]])
    pairs.append((col_ioc(y, 13), a, b))
pairs.sort(reverse=True)
print('rank of 54-55 among %d consecutive page pairs at period 13:' % len(pairs), [i for i, (v, a, b) in enumerate(pairs) if a == 54][0] + 1, ' top:', [(f'{a}-{b}', round(v, 3)) for v, a, b in pairs[:5]])
# best period per pair: how often does some period look this good by chance?
mx = []
for a, b in zip(pg, pg[1:]):
    if b != a + 1: continue
    y = dstream([r for k in (a, b) for _, r in page[k]])
    mx.append(max(col_ioc(y, P) for P in range(2, 41)))
print('max over periods 2-40, typical across pairs: median %.3f, max %.3f' % (sorted(mx)[len(mx) // 2], max(mx)))
# (b) shuffles of the same runes (keep doublet count by rejection on d stream itself)
rng = random.Random(3); obs = col_ioc(x, 13); ge = 0; R = 2000
for _ in range(R):
    z = x[:]; rng.shuffle(z)
    ge += col_ioc(z, 13) >= obs
print('shuffled d stream: P(period-13 column IoC >= %.3f) = %.3f' % (obs, ge / R))
print('\n=== other numberings ===')
for label, ks in (('full images 54-55 = pages 52-53', (52, 53)), ('unsolved-folder 54-55 = full images 71-72 = pages 69-70', (69, 70))):
    x = dstream([r for k in ks for _, r in page[k]])
    obs = col_ioc(x, 13)
    ranks = sorted(((col_ioc(x, P), P) for P in range(1, 41)), reverse=True)
    ge = sum(col_ioc(rng.sample(x, len(x)), 13) >= obs for _ in range(R))
    gmax = 0
    for _ in range(500):
        z = rng.sample(x, len(x)); gmax += max(col_ioc(z, P) for P in range(2, 41)) >= obs
    print(f'{label}: {len(x)} non-zero differences, {len(x) / 13:.0f} per column')
    print(f'   period 13 column IoC {obs:.3f}; rank among periods 1-40: {[p for v, p in ranks].index(13) + 1}; top {[(p, round(v, 3)) for v, p in ranks[:4]]}')
    print(f'   shuffles with period-13 IoC >= observed: {ge / R:.3f};  shuffles where SOME period 2-40 reaches it: {gmax / 500:.3f}')
    print(f'   segments: {sorted({s for k in ks for s, _ in page[k]})}')
