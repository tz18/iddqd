"""Crib unsolved clauses with word order free (words treated as scrambled within clauses).
Candidates: every phrase (Blake line or sentence piece, solved LP clause, signed-message sentence) whose words can be
assigned one-to-one to the clause's words with matching rune lengths, each word spelled in LP style (TH = 1 rune) or
letter by letter (T,H). Validation needs a cipher, so the test is the classic running-key check: for each placement of
the crib's words on the clause's words (up to 24 placements), derive the key under k = s - p, p - s, s + p (mod 29),
with s = the raw ciphertext or the autokey-removed stream (c[i] - c[i-1]); score the key's English-likeness (mean
rune-pair log-likelihood ratio vs uniform, models trained on Blake in both spellings; best of the two).
Control: the identical candidates and search applied to 20 fake ciphertexts for the same clause (runes drawn from the
unsolved text); per-clause p = share of fakes whose best score >= the real best. Clauses with 2-10 words."""
import os, sys, re, glob, collections, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
from lp_common import UNS, VAL, LAT, PR
src = open(os.path.join(HERE, 'sum_preserving.py')).read(); exec(src[src.index('L2I = {'):src.index('bl = re.findall')])
rng = np.random.default_rng(2026); ISP = set(PR); V = np.array(VAL)
blake = open(os.path.join(HERE, 'sources', 'blake', '_ALL.txt')).read()
# rune-pair models (key English-likeness)
def model(dig):
    m = np.ones((29, 29))
    for w in re.findall(r"[A-Za-z]+", blake):
        s = spell(w.upper(), dig)
        for a, b in zip(s[:-1], s[1:]): m[a, b] += 1
    return np.log2(m / m.sum(1, keepdims=True) * 29)
M1, M2 = model(True), model(False)
# candidate phrases
phr = set()
def add(text):
    for s in re.split(r'[\n.;:!?]+', text):
        ws = tuple(w.upper() for w in re.findall(r"[A-Za-z']+", s) if re.search('[A-Za-z]', w))
        ws = tuple(w.replace("'", "") for w in ws)
        if 2 <= len(ws) <= 10: phr.add(ws)
add(blake)
tr = open(os.path.join(ROOT, 'liber-primus__translation', 'liber-primus__translation.txt')).read()
add('\n'.join(re.sub(r'^\S+\s+', '', l) for l in tr.splitlines() if re.match(r'^\d+\.\d+', l)))
for f in glob.glob(os.path.join(ROOT, 'lp_outguessed', '*.txt')):
    t = open(f, errors='ignore').read()
    for m in re.finditer(r'Hash: \S+\s*(.*?)-----BEGIN PGP SIGNATURE', t, re.S): add(m.group(1))
add('Beware false paths. Always verify PGP signature from 7A35090F.')
PH = list(phr); print('candidate phrases:', len(PH), flush=True)
spcache = {}
def spellings(w):
    if w not in spcache:
        a, b = tuple(spell(w, True)), tuple(spell(w, False)); spcache[w] = list({a, b}) if a and b else [a or b]
    return spcache[w]
byn = collections.defaultdict(list)
for ws in PH:
    sig = [set(len(s) for s in spellings(w)) for w in ws]
    byn[len(ws)].append((ws, sig))
# unsolved clauses
cls = collections.OrderedDict(); seq = list(UNS); C = np.array([r['c'] for r in seq]); SEG = np.array([r['seg'] for r in seq])
prevc = np.r_[-1, C[:-1]]; prevc[np.r_[True, SEG[1:] != SEG[:-1]]] = -1
for i, r in enumerate(seq): cls.setdefault(r['clause'], collections.OrderedDict()).setdefault(r['word'], []).append(i)
def placements(ws, lens, limit=24):
    """random one-to-one placements of phrase words (with a spelling each) onto clause word slots of equal length"""
    out = []; slots = list(range(len(lens)))
    for _ in range(limit * 6):
        order = list(rng.permutation(len(ws))); free = set(slots); asg = {}
        ok = True
        for wi in order:
            opts = [(sp, sl) for sp in spellings(ws[wi]) for sl in free if lens[sl] == len(sp)]
            if not opts: ok = False; break
            sp, sl = opts[rng.integers(len(opts))]; asg[sl] = sp; free.discard(sl)
        if ok:
            key = tuple(asg[s] for s in slots)
            if key not in out: out.append(key)
        if len(out) >= limit: break
    return out
def best_scores(cvals, pvals_list, prev_first):
    """cvals: clause ciphertext runes (array); pvals_list: E x L plaintext arrays; returns best score and arg"""
    P = np.array(pvals_list); E, L = P.shape
    d = (cvals - np.r_[prev_first, cvals[:-1]]) % 29
    best = -9; arg = None
    for sname, s in (('raw', cvals), ('autokey-removed', d)):
        if sname != 'raw' and prev_first < 0:
            s = s.copy()
        for op in range(3):
            K = (s - P) % 29 if op == 0 else (P - s) % 29 if op == 1 else (s + P) % 29
            for M in (M1, M2):
                sc = M[K[:, :-1], K[:, 1:]].mean(1); j = int(sc.argmax())
                if sc[j] > best: best = sc[j]; arg = (sname, op, j, K[j])
    return best, arg
OPS = ['k = s - p', 'k = p - s', 'k = s + p']
report = []; pvals = []
for cid, wd in cls.items():
    words = list(wd.values()); n = len(words)
    if not 2 <= n <= 10: continue
    idx = [i for w in words for i in w]; lens = [len(w) for w in words]; cvals = C[idx]; pf = prevc[idx[0]]
    cands = []
    target = collections.Counter(lens)
    for ws, sig in byn[n]:
        # quick multiset feasibility by greedy on sorted options
        if sum(1 for s in sig if s & set(lens)) < n: continue
        pl = placements(ws, lens)
        if pl: cands.append((ws, pl))
    if not cands: continue
    if len(cands) > 400: cands = [cands[i] for i in rng.choice(len(cands), 400, replace=False)]
    rows, meta = [], []
    for ws, pl in cands:
        for p in pl: rows.append(np.concatenate([np.array(x) for x in p])); meta.append((ws, p))
    real, arg = best_scores(cvals, rows, pf)
    allc = C
    fakes = [best_scores(allc[rng.integers(0, len(allc), len(cvals))], rows, allc[rng.integers(len(allc))])[0] for _ in range(20)]
    p = (1 + sum(f >= real for f in fakes)) / 21; pvals.append(p)
    ws, plc = meta[arg[2]]; ptxt = '-'.join(''.join(LAT[x] for x in w) for w in plc)
    keytxt = ''.join(LAT[x] for x in arg[3]); psum = int(sum(V[np.concatenate([np.array(x) for x in plc])]))
    report.append((p, real, np.mean(fakes), seq[idx[0]]['page'], n, len(cands), ' '.join(ws), ptxt, arg[0], OPS[arg[1]], keytxt, psum in ISP))
    print(f"p{seq[idx[0]]['page']:2d} clause {cid:3d} ({n} words, {len(cands)} cribs): best {real:.3f} vs fakes {np.mean(fakes):.3f}, p {p:.2f}", flush=True)
pv = np.array(pvals); stat = -2 * np.log(pv).sum()
from scipy.stats import chi2
print(f'\nclauses tested {len(pv)}; clauses with p <= 0.05: {np.sum(pv <= 0.05)} (expected {0.05 * len(pv):.1f} if nothing is there; p is discrete, min 1/21)')
print(f'Fisher combined: chi2 {stat:.1f} on {2 * len(pv)} df, p {chi2.sf(stat, 2 * len(pv)):.3f}')
with open(os.path.join(HERE, 'results', 'crib_clauses_top.md'), 'w') as f:
    f.write('# Best running-key cribs per unsolved clause (word order free)\n\nColumns: per-clause p vs fake ciphertexts, best key score (bits/rune pair over uniform), fakes mean, page, words, cribs tried, crib phrase, crib as placed (plaintext runes), stream, operation, implied key (Latin), crib GP sum prime\n\n')
    for r in sorted(report)[:60]:
        f.write(f'- p {r[0]:.2f} | score {r[1]:.3f} (fakes {r[2]:.3f}) | p{r[3]} | {r[4]} words | {r[5]} cribs | **{r[6]}** | {r[7]} | {r[8]}, {r[9]} | key `{r[10]}` | prime sum: {r[11]}\n')
print('wrote results/crib_clauses_top.md')
