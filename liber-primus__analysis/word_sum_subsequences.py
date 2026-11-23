"""Does the sequence of word GP sums (unsolved text, in reading order) contain, as an ordered subsequence with
other words in between, a long run of consecutive terms of a known integer sequence?
Includes the page-30 (32.jpg) square's sequence: prime(F(n)+1) = 2,3,5,7,13,23,43,79,149,263,463,829,1481,2593,...
(each written in the square as its distance from 3301), and its 3301-minus form.
For every sequence and every starting term, greedily match consecutive terms in order, allowing gaps of up to G
words (G = any, 50, 20). Statistic: longest run of consecutive terms matched. Control: the same word sums in
shuffled order (identical values, no deliberate ordering)."""
import os, json, random, bisect
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
PR = dict(zip(GP, [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]))
words, cur, where = [], None, []
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        if not 7 <= l['s'] <= 15: continue
        for t in l['t']:
            if t[0] in '-.': cur = None; continue
            if t[0] != 'r': cur = None; continue
            if cur is None: cur = []; words.append(cur); where.append((p['page'], li))
            cur.append(t[1])
S = [sum(PR[r] for r in w) for w in words]
MAXV = max(S)
isp = lambda n: n > 1 and all(n % k for k in range(2, int(n ** .5) + 1))
P = [n for n in range(2, 20000) if isp(n)]
F = [0, 1]
while F[-1] < 10 ** 6: F.append(F[-1] + F[-2])
seqs = {}
sq = []
for f in F:
    v = P[f] if f < len(P) else None
    if v and (not sq or v != sq[-1]): sq.append(v)
seqs['square: prime(F(n)+1)'] = sq
seqs['square: 3301 - prime(F(n)+1)'] = [3301 - v for v in sq if 3301 - v > 0]
seqs['primes'] = P
seqs['Fibonacci'] = sorted(set(F[2:]))
seqs['Fibonacci primes'] = [f for f in F if isp(f)]
L = [2, 1]
while L[-1] < 10 ** 5: L.append(L[-1] + L[-2])
seqs['Lucas'] = L[1:]
T = [1, 1, 2]
while T[-1] < 10 ** 5: T.append(T[-1] + T[-2] + T[-3])
seqs['tribonacci'] = T[2:]
seqs['squares'] = [i * i for i in range(1, 200)]
seqs['cubes'] = [i ** 3 for i in range(1, 40)]
seqs['triangular'] = [i * (i + 1) // 2 for i in range(1, 200)]
seqs['powers of 2'] = [2 ** i for i in range(1, 20)]
seqs['Catalan'] = [1, 2, 5, 14, 42, 132, 429, 1430, 4862]
seqs['prime-indexed primes'] = [P[p - 1] for p in P[:200]]
seqs['twin primes (lower)'] = [p for p in P if isp(p + 2)]
seqs['Sophie Germain primes'] = [p for p in P if isp(2 * p + 1)]
seqs['emirps'] = [p for p in P if isp(int(str(p)[::-1])) and str(p) != str(p)[::-1]]
for k in list(seqs): seqs[k] = [v for v in seqs[k] if v <= MAXV]
def longest(Svals, seq, G):
    pos = {}
    for i, v in enumerate(Svals): pos.setdefault(v, []).append(i)
    best = (0, None)
    for a in range(len(seq)):
        if seq[a] not in pos: continue
        for start in pos[seq[a]]:                 # try every occurrence of the first term
            i = start; k = a + 1; chain = [start]
            while k < len(seq):
                lst = pos.get(seq[k], [])
                j = bisect.bisect_right(lst, i)
                if j == len(lst) or (G and lst[j] - i > G): break
                i = lst[j]; chain.append(i); k += 1
            if len(chain) > best[0]: best = (len(chain), (a, chain))
    return best
rng = random.Random(3)
print('word sums: %d words, values %d-%d' % (len(S), min(S), MAXV))
print('sequence                         max gap   real run   control median / 95th pct / max   p(>=real)   real match')
for name, seq in seqs.items():
    for G in (None, 50, 20):
        r, info = longest(S, seq, G)
        null = [longest(rng.sample(S, len(S)), seq, G)[0] for _ in range(100)]
        p = np.mean(np.array(null) >= r)
        ex = ''
        if info and r >= 3:
            a, chain = info; ex = f'{seq[a:a + r]} at pages {sorted({where[i][0] for i in chain})}'
        print(f'{name:32s} {str(G or "any"):>7s}   {r:8d}   {np.median(null):6.1f} / {np.percentile(null, 95):5.1f} / {max(null):3d}        {p:5.2f}   {ex}')
# zoom: the Fibonacci run with gaps <= 50
r, (a, chain) = longest(S, seqs['Fibonacci'], 50)
LAT = dict(zip(GP, ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]))
print('\nFibonacci run with gaps <= 50:')
for i in chain: print(f'   word {i:4d}  page {where[i][0]} line {where[i][1]:2d}  sum {S[i]:4d}  {"".join(words[i])}  ({"-".join(LAT[c] for c in words[i])})')
print('   gaps between them (words):', [b - a2 for a2, b in zip(chain, chain[1:])])
null = [longest(rng.sample(S, len(S)), seqs['Fibonacci'], 50)[0] for _ in range(2000)]
print('   2000 shuffles: P(run >= %d) = %.4f;  with %d sequence x gap combinations tested, expected false hits at this level: %.2f'
      % (r, np.mean(np.array(null) >= r), len(seqs) * 3, np.mean(np.array(null) >= r) * len(seqs) * 3))
