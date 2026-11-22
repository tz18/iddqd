"""Hypothesis: rotate plaintext so EA -> F (x+1), Vigenere with a period-13 key that skips F (key does not
advance on F), then ciphertext autokey c[i] = c[i-1] + s[i].
Undo autokey: d[i] = c[i] - c[i-1].  Zeros in d = skipped F (the doublets).  Drop them; the rest should be a
period-13 Vigenere: split into 13 columns, each column should have English-like IoC (~1.73)."""
import os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
def ioc(xs):
    c = collections.Counter(xs); n = len(xs)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * 29 if n > 1 else 0
segs = collections.OrderedDict()
for p in d['pages']:
    for l in p['lines']:
        if 7 <= l['s'] <= 15:
            segs.setdefault(l['s'], []).extend(IDX[t[1]] for t in l['t'] if t[0] == 'r')
def streams(per_segment, sign):
    out = []
    groups = list(segs.values()) if per_segment else [sum(segs.values(), [])]
    for g in groups:
        dd = [(sign * (g[i] - g[i - 1])) % 29 for i in range(1, len(g))]
        out.append([x for x in dd if x != 0])          # drop skipped F's
    return out
def col_ioc(groups, period):
    cols = [[] for _ in range(period)]
    for g in groups:
        for j, x in enumerate(g): cols[j % period].append(x)
    return sum(ioc(c) for c in cols) / period
for per_segment in (True, False):
    for sign in (1, -1):
        g = streams(per_segment, sign)
        res = sorted(((col_ioc(g, P), P) for P in range(1, 41)), reverse=True)
        p13 = col_ioc(g, 13)
        print(f'key restarts {"each segment" if per_segment else "never"}, d sign {sign:+d}: period 13 column IoC {p13:.3f};  best periods {[(p, round(v, 3)) for v, p in res[:4]]}')
# also without dropping zeros (if the key advances on F after all)
g = [[(s[i] - s[i - 1]) % 29 for i in range(1, len(s))] for s in segs.values()]
print('zeros kept, period 13 column IoC %.3f' % col_ioc(g, 13))
