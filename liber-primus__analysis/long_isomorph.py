"""Check the longest isomorphs in the unsolved stream against doublet-matched shuffles."""
__file__ = '/home/user/iddqd/liber-primus__analysis/isomorphs_autokey.py'
src = open(__file__).read()
exec(src.split('# ---------- isomorphs ----------')[0])
exec(src.split('# ---------- isomorphs ----------')[1].split("print('isomorphs")[0])
loc = [(p['page'], li) for p in d['pages'] for li, l in enumerate(p['lines']) if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
def stat(s):
    """(number of window pairs at L=12,>=4 repeats, at L=15,>=5 repeats)"""
    return (sum(len(v) - 1 for v in isomorphs(s, 12, 4).values()), sum(len(v) - 1 for v in isomorphs(s, 15, 5).values()))
real = stat(U)
for pt, pos in isomorphs(U, 15, 5).items():
    print('L15 isomorph', ''.join('abcdefghijklmnopq'[x] for x in pt), [(i, loc[i]) for i in pos], 'distance', pos[1] - pos[0])
    for i in pos: print('   ', ''.join(GP[x] for x in U[i:i + 15]))
null = []  # [stat(shuffled_no_doublets(U)) for _ in range(60)]
print('real', real)
# print('shuffles with >= real at L12/4:', sum(n[0] >= real[0] for n in null), '/60;  at L15/5:', sum(n[1] >= real[1] for n in null), '/60')
# exact extent of the match
A, B = 3067, 12272
s = 0
while pattern(U[A - s - 1:A + 15]) == pattern(U[B - s - 1:B + 15]): s += 1
e = 15
while pattern(U[A - s:A + e + 1]) == pattern(U[B - s:B + e + 1]): e += 1
A, B, L = A - s, B - s, e + s
print('full isomorph: start', A, B, 'length', L, 'pages', loc[A], loc[B])
print('  ', ''.join(GP[x] for x in U[A:A + L])); print('  ', ''.join(GP[x] for x in U[B:B + L]))
print('   pattern', ''.join('abcdefghijklmnopqrstuvwxyz'[x] for x in pattern(U[A:A + L])), 'repeated positions', L - len(set(U[A:A + L])))
more = [sum(len(v) - 1 for v in isomorphs(shuffled_no_doublets(U), 15, 5).values()) for _ in range(300)]
print('L15/5 isomorph in shuffles:', sum(x >= 1 for x in more), '/300')
