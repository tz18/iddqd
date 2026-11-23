"""Word-length sequences: exact repeats ("isomorphs"), equality-pattern isomorphs, palindromes.
Runes: exact palindromes and reversed isomorphs (a window's repeat pattern appearing later reversed).
Controls: word order shuffled (word lengths); runes shuffled keeping the doublet shortage (runes)."""
import os, json, random, collections
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
words, loc, cur = [], [], None
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        if not 7 <= l['s'] <= 15: continue
        for t in l['t']:
            if t[0] in '-.': cur = None; continue
            if t[0] != 'r': cur = None; continue
            if cur is None: cur = []; words.append(cur); loc.append((p['page'], li))
            cur.append(IDX[t[1]])
WL = [len(w) for w in words]; U = [c for w in words for c in w]
rng = random.Random(11)
def pattern(w):
    m = {}; return tuple(m.setdefault(c, len(m)) for c in w)
def pz(obs, null):
    m = sum(null) / len(null); sd = (sum((x - m) ** 2 for x in null) / len(null)) ** .5 or 1
    return f'real {obs}  shuffled {m:.1f} ± {sd:.1f}  p(>=) {sum(x >= obs for x in null) / len(null):.2f}'
# ---------- word lengths ----------
def wl_repeats(seq, W):
    g = collections.defaultdict(list)
    for i in range(len(seq) - W + 1): g[tuple(seq[i:i + W])].append(i)
    return {k: v for k, v in g.items() if len(v) > 1}
def wl_isos(seq, W, minrep):
    g = collections.defaultdict(list)
    for i in range(len(seq) - W + 1):
        pt = pattern(seq[i:i + W])
        if W - len(set(pt)) >= minrep: g[pt].append(i)
    return {k: v for k, v in g.items() if len(v) > 1}
def wl_pals(seq, minlen):
    """count maximal palindromic runs of word lengths with length >= minlen"""
    n = 0; best = (0, None)
    for c in range(len(seq)):
        for odd in (1, 0):
            l, r = (c - 1, c + 1) if odd else (c, c + 1)
            while l >= 0 and r < len(seq) and seq[l] == seq[r]: l -= 1; r += 1
            L = r - l - 1
            if L >= minlen: n += 1
            if L > best[0]: best = (L, l + 1)
    return n, best
print('WORD LENGTHS (%d words)' % len(WL))
for W in (8, 10, 12):
    real = sum(len(v) - 1 for v in wl_repeats(WL, W).values())
    null = [sum(len(v) - 1 for v in wl_repeats(rng.sample(WL, len(WL)), W).values()) for _ in range(200)]
    print(f'  exact repeated length-sequences of {W} words: {pz(real, null)}')
for W, mr in ((10, 6), (14, 9)):
    real = sum(len(v) - 1 for v in wl_isos(WL, W, mr).values())
    null = [sum(len(v) - 1 for v in wl_isos(rng.sample(WL, len(WL)), W, mr).values()) for _ in range(100)]
    print(f'  equality-pattern isomorphs, {W} words, >= {mr} repeats: {pz(real, null)}')
n, best = wl_pals(WL, 9)
nulls = [wl_pals(rng.sample(WL, len(WL)), 9) for _ in range(200)]
print(f'  palindromes of >= 9 word lengths: {pz(n, [x[0] for x in nulls])}')
print(f'  longest word-length palindrome: {best[0]} words at word {best[1]} {loc[best[1]]}: {WL[best[1]:best[1] + best[0]]};  shuffled longest: median {sorted(x[1][0] for x in nulls)[100]}, max {max(x[1][0] for x in nulls)}')
# ---------- runes ----------
def shuffled_no_doublets(s):
    a = s[:]; rng.shuffle(a); target = sum(x == y for x, y in zip(s, s[1:]))
    while True:
        dbl = [i for i in range(1, len(a)) if a[i] == a[i - 1]]
        if len(dbl) <= target: return a
        i = rng.choice(dbl); j = rng.randrange(len(a)); a[i], a[j] = a[j], a[i]
def rune_pals(s):
    lens = collections.Counter(); best = (0, 0)
    for c in range(len(s)):
        for odd in (1, 0):
            l, r = (c - 1, c + 1) if odd else (c, c + 1)
            while l >= 0 and r < len(s) and s[l] == s[r]: l -= 1; r += 1
            L = r - l - 1
            lens[L] += 1
            if L > best[0]: best = (L, l + 1)
    return lens, best
def rev_isos(s, W, minrep):
    g = collections.defaultdict(list)
    for i in range(len(s) - W + 1):
        w = s[i:i + W]
        if W - len(set(w)) >= minrep: g[pattern(w)].append(i)
    hits = []
    for i in range(len(s) - W + 1):
        w = s[i:i + W]
        if W - len(set(w)) < minrep: continue
        for j in g.get(pattern(w[::-1]), []):
            if j > i + W: hits.append((i, j))
    return hits
print('\nRUNES (%d)' % len(U))
lens, best = rune_pals(U)
N = [rune_pals(shuffled_no_doublets(U)) for _ in range(20)]
for L in (5, 6, 7):
    real = sum(v for k, v in lens.items() if k >= L)
    print(f'  rune palindromes of length >= {L}: {pz(real, [sum(v for k, v in x[0].items() if k >= L) for x in N])}')
print(f'  longest rune palindrome: {best[0]} at {best[1]} {"".join(GP[x] for x in U[best[1]:best[1] + best[0]])};  shuffled longest: {sorted(x[1][0] for x in N)}')
for W, mr in ((10, 3), (12, 4), (15, 5)):
    real = len(rev_isos(U, W, mr))
    null = [len(rev_isos(shuffled_no_doublets(U), W, mr)) for _ in range(20)]
    print(f'  reversed isomorphs, window {W}, >= {mr} repeats: {pz(real, null)}')
    if W == 15:
        for i, j in rev_isos(U, W, mr)[:5]: print('     ', ''.join(GP[x] for x in U[i:i + W]), '...', ''.join(GP[x] for x in U[j:j + W]), 'distance', j - i)
