"""Exact repeated rune sequences in the unsolved stream (the isomorph search skipped patterns with no
internal repeats, e.g. DJUBEI = abcdef). Compare counts to frequency/doublet-matched shuffles."""
import os, json, collections, random
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
LAT = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
U, loc, wordpos = [], [], []
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        if not 7 <= l['s'] <= 15: continue
        k = 0
        for t in l['t']:
            if t[0] in '-.': k = 0; continue
            if t[0] != 'r': continue
            U.append(IDX[t[1]]); loc.append((p['page'], li)); wordpos.append(k); k += 1
def repeats(s, L):
    g = collections.defaultdict(list)
    for i in range(len(s) - L + 1): g[tuple(s[i:i + L])].append(i)
    return {k: v for k, v in g.items() if len(v) > 1}
rng = random.Random(5)
def shuffled(s):
    a = s[:]; rng.shuffle(a); target = sum(x == y for x, y in zip(s, s[1:]))
    while True:
        dbl = [i for i in range(1, len(a)) if a[i] == a[i - 1]]
        if len(dbl) <= target: return a
        i = rng.choice(dbl); j = rng.randrange(len(a)); a[i], a[j] = a[j], a[i]
for L in (4, 5, 6, 7):
    real = repeats(U, L); nr = sum(len(v) - 1 for v in real.values())
    nulls = [sum(len(v) - 1 for v in repeats(shuffled(U), L).values()) for _ in range(20)]
    m = sum(nulls) / len(nulls)
    print(f'length {L}: repeated sequences {nr}   shuffled {m:.1f} (max {max(nulls)})')
print('\nall exact repeats of length >= 5:')
for L in (7, 6, 5):
    for k, v in repeats(U, L).items():
        print(f'  len {L}', ''.join(GP[x] for x in k), '-'.join(LAT[x] for x in k), [(i, loc[i], 'word pos', wordpos[i]) for i in v], 'distance', [b - a for a, b in zip(v, v[1:])])
