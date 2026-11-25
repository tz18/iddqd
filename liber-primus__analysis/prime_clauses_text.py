"""The solved Liber Primus plaintext reduced to its clauses whose GP sum is prime (non-prime clauses dropped),
by section, in rune transliteration (C = K/C, U = V/U, NG = NG/ING, IA = IO). Writes results/prime_clauses_text.md."""
import os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, VAL, LAT, d, PR
P = set(PR); out = []
cl = collections.OrderedDict()
for r in R:
    if d['segments'][r['seg']]['solved']: cl.setdefault(r['clause'], []).append(r)
cur = None; kept = total = 0
for rs in cl.values():
    sec = d['segments'][rs[0]['seg']]['name']
    if sec != cur: out.append(f'\n## {sec}  (pages {rs[0]["page"]}+)\n'); cur = sec
    ws = collections.OrderedDict()
    for r in rs: ws.setdefault(r['word'], []).append(LAT[r['p']])
    s = sum(VAL[r['p']] for r in rs); total += 1
    if s in P: kept += 1; out.append(f'{" ".join("".join(w) for w in ws.values())}  ({s})')
txt = f'# Liber Primus, solved text, prime clauses only\n\n{kept} of {total} clauses have a prime GP sum.\n' + '\n'.join(out) + '\n'
open(os.path.join(HERE, 'results', 'prime_clauses_text.md'), 'w').write(txt); print(txt)
