"""Cipher-agnostic crib test: does the unsolved text contain a sentence of Blake's 'The Marriage of Heaven and
Hell' (used by Cicada in 2012)? Word breaks are visible in the ciphertext, so a quoted sentence would show up as
an exact run of word lengths (in runes). Rune spelling: TH, NG/ING single runes; EA, EO, OE, AE, IA, IO may be one
or two runes (both allowed). Each Blake sentence/clause (>= 5 words) is slid along the unsolved word-length
sequence; a hit needs every word length to be possible. Control: the same search against shuffled word orders."""
import os, re, json, random, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
words, where, cur = [], [], None
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        if not 7 <= l['s'] <= 15: continue
        for t in l['t']:
            if t[0] in '-.': cur = None; continue
            if t[0] != 'r': cur = None; continue
            if cur is None: cur = []; words.append(cur); where.append((p['page'], li))
            cur.append(t[1])
WL = [len(w) for w in words]
def rune_lengths(word):
    w = re.sub("[^A-Z]", "", word.upper()).replace('ING', '#').replace('TH', '#').replace('NG', '#').replace('QU', 'CW')
    n_fixed = len(w)
    opt = len(re.findall('EA|EO|OE|AE|IA|IO', w))        # each optional digraph may save one rune
    return set(range(n_fixed - opt, n_fixed + 1))
txt = open(os.path.join(HERE, 'sources', 'blake_marriage_of_heaven_and_hell.txt')).read()
clauses = [c.strip() for c in re.split(r'[.;:!?]', txt) if c.strip()]
cl = []
for c in clauses:
    ws = [w for w in re.findall(r"[A-Za-z']+", c) if re.sub("[^A-Za-z]", "", w)]
    if len(ws) >= 5: cl.append((c, [rune_lengths(w) for w in ws]))
def search(wl, clist, minw):
    hits = []
    wl = np.array(wl)
    for c, L in clist:
        if len(L) < minw: continue
        n = len(L)
        for i in range(len(wl) - n + 1):
            if all(wl[i + k] in L[k] for k in range(n)): hits.append((n, c, i))
    return hits
rng = random.Random(5)
for minw in (5, 6, 7, 8, 10):
    real = search(WL, cl, minw)
    null = [len(search(rng.sample(WL, len(WL)), cl, minw)) for _ in range(30)]
    print(f'clauses with >= {minw} words: real hits {len(real)}, shuffled word order mean {np.mean(null):.1f} (max {max(null)}), p(>=real) {np.mean(np.array(null) >= len(real)):.2f}')
    if minw >= 7:
        for n, c, i in sorted(real, reverse=True)[:5]: print(f'     {n} words at word {i} (page {where[i][0]}): "{c[:90]}"')
print('Blake clauses tested:', len(cl))
