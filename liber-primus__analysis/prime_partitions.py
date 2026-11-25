"""(1) Can each solved plaintext clause be cut on word boundaries into consecutive pieces whose GP sums are all
prime? Dynamic programming over words: the partition with the fewest pieces (ties: show one). Null: the same
clause with its runes shuffled within the solved text (word lengths kept), 2000 draws: how often a partition exists
and how few pieces it needs.
(2) Every unsolved clause whose ciphertext GP sum is prime: runes, Latin letters, page/line, length, sum."""
import os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, VAL, LAT, GP, d, PR, UNS
isp = np.zeros(400000, bool); isp[PR] = True; rng = np.random.default_rng(13)
def best_partition(ws):          # ws: list of word sums -> (min pieces, cut list) or None
    n = len(ws); pre = np.r_[0, np.cumsum(ws)]; best = [None] * (n + 1); best[0] = (0, [])
    for j in range(1, n + 1):
        for i in range(j):
            if best[i] is not None and isp[pre[j] - pre[i]]:
                cand = (best[i][0] + 1, best[i][1] + [j])
                if best[j] is None or cand[0] < best[j][0]: best[j] = cand
    return best[n]
def words_of(rs, f):
    ws = collections.OrderedDict()
    for r in rs: ws.setdefault(r['word'], []).append(r)
    return [[f(r) for r in w] for w in ws.values()], list(ws.values())
S = [r for r in R if d['segments'][r['seg']]['solved']]
pool = np.array([r['p'] for r in S]); V = np.array(VAL)
cl = collections.OrderedDict()
for r in S: cl.setdefault(r['clause'], []).append(r)
print('=== (1) solved plaintext clauses cut into all-prime pieces on word boundaries')
tot_real = tot_null = 0; rows = []
for k, rs in cl.items():
    wsv, wrs = words_of(rs, lambda r: r['p']); sums = [sum(VAL[x] for x in w) for w in wsv]
    bp = best_partition(sums); L = [len(w) for w in wsv]
    nulls = []
    for _ in range(300):
        y = rng.choice(pool, sum(L)); s = np.add.reduceat(V[y], np.r_[0, np.cumsum(L)[:-1]]); b = best_partition(list(s))
        nulls.append(b[0] if b else 99)
    nulls = np.array(nulls)
    txt = [''.join(LAT[x] for x in w) for w in wsv]
    if bp:
        cuts = [0] + bp[1]; pieces = [' '.join(txt[a:b]) + f' ({sum(sums[a:b])})' for a, b in zip(cuts, cuts[1:])]
    rows.append((len(wsv), bp[0] if bp else None, np.mean(nulls < 99), np.mean(nulls <= (bp[0] if bp else 0)) if bp else None,
                 ' | '.join(pieces) if bp else 'NO PARTITION: ' + ' '.join(txt)))
for nw, k, pn, pk, s in rows:
    if nw >= 6:
        print(f'{nw:2d} words -> {str(k):>4s} pieces | null: partition exists {pn:.2f}, this few pieces {pk if pk is None else round(pk, 2)}\n      {s}')
ex = [r for r in rows if r[0] >= 6]
print(f'\nclauses with >= 6 words: {len(ex)}, partitionable {sum(r[1] is not None for r in ex)}, '
      f'expected under null {sum(r[2] for r in ex):.1f}; mean min pieces real {np.mean([r[1] for r in ex if r[1]]):.2f}')
print('\n=== (2) unsolved clauses with prime ciphertext GP sums')
cu = collections.OrderedDict()
for r in UNS: cu.setdefault(r['clause'], []).append(r)
for k, rs in cu.items():
    s = sum(VAL[r['c']] for r in rs)
    if isp[s]:
        wsv, _ = words_of(rs, lambda r: r['c'])
        print(f"p{rs[0]['page']:2d} L{rs[0]['line']:2d}-L{rs[-1]['line']:2d} seg{rs[0]['seg']:2d}  {len(rs):3d} runes  sum {s:5d}  "
              f"{'-'.join(''.join(GP[x] for x in w) for w in wsv)}\n{'':38s}{'-'.join(''.join(LAT[x] for x in w) for w in wsv)}")
