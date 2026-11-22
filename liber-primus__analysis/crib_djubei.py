"""Crib DJU BEI (p42 line 1 and p70 line 3).
1) Search key-stream families (primes, totient(primes), Fibonacci, GP primes cycling, position) with any start offset,
   indexed by position in the unsolved stream / in the segment / on the page; subtract or add; optional atbash.
   Keep settings where BOTH copies decrypt to a pair of real 3-rune words.
2) List plausible English 3+3 cribs with the additive key they imply at each copy."""
import os, re, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
LAT = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
PR = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
table = sorted([(l, i) for i, l in enumerate(LAT)] + [("K", 5), ("V", 1), ("Q", 5), ("Z", 15), ("IO", 27), ("ING", 21)], key=lambda t: -len(t[0]))
def runes(w):
    out, i = [], 0
    while i < len(w):
        m = next(((s, v) for s, v in table if w.startswith(s, i)), None)
        if m: out.append(m[1]); i += len(m[0])
        else: i += 1
    return tuple(out)
vocab = set(open('/home/user/idkfa/data/dict').read().upper().split()) if os.path.exists('/home/user/idkfa/data/dict') else set()
vocab |= set(re.findall('[A-Z]+', open(os.path.join(HERE, '..', 'liber-primus__translation', 'liber-primus__translation.txt')).read()))
W3 = {}
for w in vocab:
    r = runes(w)
    if len(r) == 3: W3.setdefault(r, w)
print('3-rune English words in vocabulary:', len(W3))
# positions of every unsolved rune
stream = []
segc = collections.Counter(); pagec = collections.Counter()
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        if not 7 <= l['s'] <= 15: continue
        for t in l['t']:
            if t[0] == 'r':
                stream.append((IDX[t[1]], len(stream), segc[l['s']], pagec[p['page']], p['page'], li))
                segc[l['s']] += 1; pagec[p['page']] += 1
U = [s[0] for s in stream]
occ = [i for i in range(len(U) - 5) if U[i:i + 6] == [IDX[c] for c in 'ᛞᛄᚢᛒᛖᛁ']]
print('occurrences (global index):', occ)
primes = []; n = 2
while len(primes) < 40000:
    if all(n % q for q in primes if q * q <= n): primes.append(n)
    n += 1
fib = [0, 1]
while len(fib) < 40000: fib.append((fib[-1] + fib[-2]) % 29)
streams = {'primes': [p % 29 for p in primes], 'totient(primes)': [(p - 1) % 29 for p in primes], 'fibonacci': fib,
           'GP prime of n': [PR[i % 29] % 29 for i in range(40000)], 'n': [i % 29 for i in range(40000)]}
hits = []
for sname, S in streams.items():
    for coord, ci in (('unsolved stream', 1), ('segment', 2), ('page', 3)):
        for off in range(0, 20000):
            for inv in (0, 1):
                for sgn in (1, -1):
                    words = []
                    for o in occ:
                        pos = [stream[o + k][ci] + off for k in range(6)]
                        pt = tuple(((28 - U[o + k] if inv else U[o + k]) - sgn * S[pos[k]]) % 29 for k in range(6))
                        words.append(pt)
                    if all(w[:3] in W3 and w[3:] in W3 for w in words):
                        hits.append((sname, coord, off, inv, sgn, [W3[w[:3]] + ' ' + W3[w[3:]] for w in words]))
print('\nkey-stream hits where both copies decrypt to two real words: %d' % len(hits))
for h in hits[:20]: print('  ', h)
# 2) plausible cribs and implied keys
cribs = ['OUR OWN', 'AND YOU', 'SEE YOU', 'YOU ARE', 'FOR YOU', 'FOR ALL', 'ALL ARE', 'AND ALL', 'NOT ONE', 'HIS OWN',
         'WAS NOT', 'ARE NOT', 'YOU MAY', 'ONE DAY', 'GOD WAS', 'THE END', 'AN END', 'ALL OUR', 'OUR WAY', 'YOU CAN', 'WHO ARE', 'ARE ONE']
ct = [IDX[c] for c in 'ᛞᛄᚢᛒᛖᛁ']
print('\nplausible cribs (3+3 runes) and the additive key c - p they imply (same at both copies, since the ciphertext is identical):')
for c in cribs:
    a, b = c.split()
    r = runes(a) + runes(b)
    if len(runes(a)) != 3 or len(runes(b)) != 3: continue
    k = [(ct[i] - r[i]) % 29 for i in range(6)]
    print(f'   {c:8s} key {k}  as runes {"".join(GP[x] for x in k)}  ({"-".join(LAT[x] for x in k)})')
# 3) running key from the solved text: does any 3+3 crib imply a key that occurs in the translations?
tr = open(os.path.join(HERE, '..', 'liber-primus__translation', 'liber-primus__translation.txt'), encoding='utf-8').read()
body = " ".join(l.split("\t")[-1] for l in tr.splitlines() if re.match(r"\s*0\.\d+\.\d+\.\d+", l))
solved = [x for w in re.findall('[A-Z]+', body) for x in runes(w)]
sidx = collections.defaultdict(list)
for i in range(len(solved) - 5): sidx[tuple(solved[i:i + 6])].append(i)
found = []
words3 = list(W3.items())
for ra, wa in words3:
    for rb, wb in words3:
        p = ra + rb
        for op, f in (('c-p', lambda c, x: (c - x) % 29), ('p-c', lambda c, x: (x - c) % 29), ('c+p', lambda c, x: (c + x) % 29)):
            k = tuple(f(ct[i], p[i]) for i in range(6))
            if k in sidx: found.append((wa + ' ' + wb, op, sidx[k][:3], '-'.join(LAT[x] for x in k)))
print('\nrunning-key check: %d cribs x 3 ops against %d solved runes -> %d hits (about %.1f expected by chance)'
      % (len(words3) ** 2, len(solved), len(found), len(words3) ** 2 * 3 * len(solved) / 29 ** 6))
for f in found[:15]: print('  ', f)
