"""Sequence-agnostic search for structure among word GP sums (unsolved text).
Null: runes shuffled across words, word lengths kept (same sum distribution, no deliberate relations).
(1) longest chain of words (each within G words of the previous) whose sums form an arithmetic progression
    (constant difference, including 0); also count of AP chains of length >= 4
(2) distance between repeats of the same sum value: spikes at any one distance
(3) correlation between sums k words apart (k=1..50); dependence between residues mod 2/3/5/29 at gaps 1..10
(4) trends with position in the text / page / line"""
import os, json, collections, math, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
PR = dict(zip(GP, [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]))
words, meta, cur = [], [], None
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        if not 7 <= l['s'] <= 15: continue
        wi_line = 0
        for t in l['t']:
            if t[0] in '-.': cur = None; continue
            if t[0] != 'r': cur = None; continue
            if cur is None:
                cur = []; words.append(cur); meta.append((p['page'], li, wi_line)); wi_line += 1
            cur.append(t[1])
lens = [len(w) for w in words]; runes = [r for w in words for r in w]
def sums_of(rs):
    out, i = [], 0
    for L in lens: out.append(sum(PR[r] for r in rs[i:i + L])); i += L
    return np.array(out)
S = sums_of(runes)
rng = random.Random(1)
def shuffled():
    r = runes[:]; rng.shuffle(r); return sums_of(r)
G = 5
def ap_stats(s):
    """longest AP chain with position gaps <= G, and number of chains reaching length >= 4"""
    n = len(s); best = 1; L = [dict() for _ in range(n)]; n4 = 0
    for j in range(n):
        for i in range(max(0, j - G), j):
            dlt = int(s[j] - s[i]); v = L[i].get(dlt, 1) + 1
            if v > L[j].get(dlt, 0): L[j][dlt] = v
            best = max(best, v)
        n4 += sum(1 for v in L[j].values() if v >= 4)
    return best, n4
def repeat_distance_peak(s, maxd=300):
    pos = collections.defaultdict(list)
    for i, v in enumerate(s): pos[int(v)].append(i)
    h = np.zeros(maxd + 1)
    for ps in pos.values():
        for a in range(len(ps)):
            for b in range(a + 1, len(ps)):
                dd = ps[b] - ps[a]
                if dd <= maxd: h[dd] += 1
    h = h[1:]; z = (h - h.mean()) / (h.std() or 1)
    return float(z.max()), int(np.argmax(z) + 1)
def lag_corr(s, K=50):
    x = (s - s.mean()) / s.std(); return np.array([np.mean(x[:-k] * x[k:]) for k in range(1, K + 1)])
def mod_dep(s):
    worst = 0
    for m in (2, 3, 5, 29):
        r = s % m
        for g in range(1, 11):
            tab = np.zeros((m, m))
            np.add.at(tab, (r[:-g], r[g:]), 1)
            e = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
            chi = ((tab - e) ** 2 / np.where(e > 0, e, 1)).sum(); df = (m - 1) ** 2
            worst = max(worst, (chi - df) / math.sqrt(2 * df))
    return worst
def trends(s):
    pos_text = np.arange(len(s)); pos_line = np.array([m[2] for m in meta])
    out = {}
    for name, x in (('position in text', pos_text), ('word position in line', pos_line)):
        out[name] = float(np.corrcoef(x, s)[0, 1])
    return out
stats = lambda s: (*ap_stats(s), *repeat_distance_peak(s), float(np.abs(lag_corr(s)).max()), mod_dep(s))
real = stats(S)
N = 60
null = [stats(shuffled()) for _ in range(N)]
names = ['longest AP chain (gaps <= %d)' % G, 'AP chains of length >= 4', 'repeat-distance spike (z)', '  at distance',
         'max |correlation| at lags 1-50', 'max residue dependence (z, mod 2/3/5/29, gaps 1-10)']
print('word GP sums: %d words; control = %d shuffles of runes across words' % (len(S), N))
for k, nm in enumerate(names):
    if nm.strip().startswith('at distance'): print(f'   {nm:52s} {real[k]}'); continue
    col = np.array([x[k] for x in null]); p = np.mean(col >= real[k])
    print(f'   {nm:52s} real {real[k]:8.3f}   control median {np.median(col):8.3f}  max {col.max():8.3f}   p(>=real) {p:.2f}')
tr = trends(S)
for k, v in tr.items():
    nullv = [trends(shuffled())[k] for _ in range(100)]
    print(f'   trend with {k:28s} r = {v:+.3f}   control |r| 95th pct {np.percentile(np.abs(nullv), 95):.3f}')
# show the longest AP chain in the real text
n = len(S); L = [dict() for _ in range(n)]; prev = [dict() for _ in range(n)]
for j in range(n):
    for i in range(max(0, j - G), j):
        dlt = int(S[j] - S[i]); v = L[i].get(dlt, 1) + 1
        if v > L[j].get(dlt, 0): L[j][dlt] = v; prev[j][dlt] = i
end = max(((L[j][dl], j, dl) for j in range(n) for dl in L[j]), default=None)
chain = []; j, dl = end[1], end[2]
while True:
    chain.append(j)
    if dl not in prev[j]: break
    j = prev[j][dl]
chain = chain[::-1]
print('   longest AP chain in the real text: sums', [int(S[i]) for i in chain], 'step', end[2], 'at words', chain, 'pages', sorted({meta[i][0] for i in chain}))
