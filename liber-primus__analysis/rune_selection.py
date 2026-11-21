"""Rune-level chaffing: if only runes at certain positions carry (mono-alphabetic) plaintext,
the selected subsequence should have English-like IoC (~1.7) instead of ~1.0.
Also tries 'numbers are the direction': solved-text word sums used as steps or keys."""
__file__ = '/home/user/iddqd/liber-primus__analysis/isomorphs_autokey.py'
exec(open(__file__).read().split('# ---------- isomorphs ----------')[0])
import itertools
def ioc(xs):
    c = collections.Counter(xs); n = len(xs)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * 29
def isp(n):
    if n < 2: return False
    return all(n % q for q in range(2, int(n ** .5) + 1))
N = len(U)
rules = {}
rules['prime positions (global)'] = [i for i in range(N) if isp(i)]
rules['prime positions (1-based)'] = [i for i in range(N) if isp(i + 1)]
f = [1, 2]
while f[-1] < N: f.append(f[-1] + f[-2])
rules['fibonacci positions'] = [x for x in f if x < N]
rules['square positions'] = [i * i for i in range(int(N ** .5) + 1) if i * i < N]
rules['rune value is prime index'] = [i for i in range(N) if isp(U[i])]
rules['after a doublet (next 20)'] = sorted({j for i in range(1, N) if U[i] == U[i - 1] for j in range(i + 1, min(N, i + 21))})
words = []
for p in d['pages']:
    for l in p['lines']:
        if not 7 <= l['s'] <= 15: continue
        for t in l['t']:
            if t[0] in '-.': words.append(None)
            elif t[0] == 'r': words.append(1)
# word starts / ends in stream coordinates
starts, ends, k, prev = [], [], 0, None
for x in words:
    if x == 1:
        if prev is None: starts.append(k)
        k += 1
    elif prev == 1: ends.append(k - 1)
    prev = x
rules['first rune of each word'] = starts
rules['last rune of each word'] = ends
for m in range(2, 31):
    for r in range(m):
        rules[f'pos ≡ {r} mod {m}'] = list(range(r, N, m))
out = []
for name, pos in rules.items():
    if len(pos) < 60: continue
    out.append((ioc([U[i] for i in pos]), len(pos), name))
out.sort(reverse=True)
print('highest IoC among %d selection rules (random 1.00, English ~1.73):' % len(out))
for v, n, name in out[:8]: print(f'   {v:.3f}  n={n:5d}  {name}')
for v, n, name in out:
    if not name.startswith('pos ≡'): print(f'   {v:.3f}  n={n:5d}  {name}')
# ---- "their numbers are the direction": solved word sums as steps / keys ----
PRV = {i: PR[i] for i in range(29)}
solved_words = []
for p in d['pages']:
    for l in p['lines']:
        if l['s'] in (0, 1, 2, 3, 4, 5, 6):
            cur = None
            for t in l['t']:
                if t[0] in '-.': cur = None; continue
                if t[0] != 'r': continue
                if cur is None: cur = []; solved_words.append(cur)
                cur.append(IDX[t[1]])
ws = [sum(PR[x] for x in w) for w in solved_words]
print('\nsolved word sums (first 12):', ws[:12], '... n =', len(ws))
pos, acc = [], 0
for s in ws:
    acc += s
    if acc >= N: break
    pos.append(acc)
print('cumulative solved word sums as positions: n=%d IoC %.3f' % (len(pos), ioc([U[i] for i in pos])))
pos2 = [s % N for s in ws]; print('word sums as positions: IoC %.3f' % ioc([U[i] for i in pos2]))
for name, key in (('word sum mod 29, one per rune', [s % 29 for s in ws]),):
    for sg in (1, -1):
        xs = [(U[i] - sg * key[i % len(key)]) % 29 for i in range(N)]
        print(f'{name} ({"-" if sg>0 else "+"}): IoC {ioc(xs):.3f}')
# per-word key: shift every rune of the k-th unsolved word by the k-th solved word sum
uw = []; cur = None
for p in d['pages']:
    for l in p['lines']:
        if not 7 <= l['s'] <= 15: continue
        for t in l['t']:
            if t[0] in '-.': cur = None; continue
            if t[0] != 'r': continue
            if cur is None: cur = []; uw.append(cur)
            cur.append(IDX[t[1]])
for sg in (1, -1):
    xs = [(c - sg * ws[k % len(ws)]) % 29 for k, w in enumerate(uw) for c in w]
    print(f'shift each unsolved word by a solved word sum ({"-" if sg>0 else "+"}): IoC {ioc(xs):.3f}')
# plaintext frequency check for the autokey idea: which plaintext rune has frequency ~0.66%?
solved_plain = stream_for((2, 4, 6, 17))
c = collections.Counter(solved_plain); n = len(solved_plain)
print('\nplain-rune frequencies nearest the 0.66%% doublet rate:', sorted(((abs(v / n - .0066), GP[k], round(v / n * 100, 2)) for k, v in c.items()))[:5], 'F =', round(c[0] / n * 100, 2), '%')
up = sorted(set(pos2)); print('word sums as positions, duplicates removed: n=%d IoC %.3f' % (len(up), ioc([U[i] for i in up])))
