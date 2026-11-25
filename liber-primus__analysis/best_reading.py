"""Best-reading test of the GP-sum codebook. Each unsolved word (ciphertext as written) is replaced by any Blake word
with the same GP sum. Score the most English-like choice: (a) unigram: each word independently, the most frequent
candidate; (b) bigram: Viterbi over candidate lattices with a Blake word-pair model (add-0.1 smoothing, backoff to
unigram). Score = mean log2-probability per covered word. Compare with fake texts: same word lengths, unsolved runes
shuffled (30 fakes). Codebooks: all Blake words and Urizen words, LP spelling and letter by letter.
The bigram score uses the written word order."""
import os, sys, re, collections, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import UNS, VAL
src = open(os.path.join(HERE, 'sum_preserving.py')).read(); exec(src[src.index('L2I = {'):src.index('bl = re.findall')])
V = np.array(VAL); rng = np.random.default_rng(12)
toks = [w.upper() for w in re.findall(r"[A-Za-z]+", open(os.path.join(HERE, 'sources', 'blake', '_ALL.txt')).read())]
uni = collections.Counter(toks); N = sum(uni.values()); big = collections.Counter(zip(toks[:-1], toks[1:]))
def lu(w): return math.log2((uni[w] + 0.1) / (N + 0.1 * len(uni)))
def lb(a, b): return math.log2((big[(a, b)] + 0.1 * (uni[b] + 0.1) / N * 50) / (uni[a] + 5)) if a else lu(b)
uw = collections.OrderedDict(); clause_of = {}
for r in UNS: uw.setdefault(r['word'], []).append(r['c']); clause_of[r['word']] = r['clause']
W = list(uw.values()); WC = [clause_of[k] for k in uw]; lens = [len(w) for w in W]; allc = np.array([x for w in W for x in w])
def fake():
    x = rng.permutation(allc); out, i = [], 0
    for L in lens: out.append(x[i:i + L]); i += L
    return out
def run(words, cand):
    sums = [int(V[w].sum()) for w in words]
    uni_scores = [max(lu(c) for c in cand[s]) for s in sums if s in cand]
    # Viterbi bigram along the sequence (covered words only; gaps break the chain)
    total = 0; n = 0; prev = {None: 0.0}
    for s in sums:
        if s not in cand: prev = {None: 0.0}; continue
        cs = sorted(cand[s], key=lambda c: -uni[c])[:30]
        cur = {c: max(pv + lb(p, c) for p, pv in prev.items()) for c in cs}
        best_prev_total = max(prev.values())
        total += max(cur.values()) - best_prev_total; n += 1; prev = cur
    return np.mean(uni_scores), total / n
for book in ('_ALL', 'The_Book_of_Urizen'):
    vocab = set(w.upper() for w in re.findall(r"[A-Za-z]+", open(os.path.join(HERE, 'sources', 'blake', book + '.txt')).read()))
    for dig in (True, False):
        cand = collections.defaultdict(list)
        for w in vocab: cand[int(sum(VAL[x] for x in spell(w, dig)))].append(w)
        real = run(W, cand); nl = np.array([run(fake(), cand) for _ in range(30)])
        lab = f'{"all Blake" if book == "_ALL" else "Urizen"}, {"LP spelling" if dig else "letter by letter"}'
        print(f'{lab:30s} unigram best {real[0]:7.3f} (fakes {nl[:, 0].mean():7.3f} +/- {nl[:, 0].std():.3f}, z {(real[0] - nl[:, 0].mean()) / nl[:, 0].std():+.2f}) | '
              f'bigram best {real[1]:7.3f} (fakes {nl[:, 1].mean():7.3f} +/- {nl[:, 1].std():.3f}, z {(real[1] - nl[:, 1].mean()) / nl[:, 1].std():+.2f})', flush=True)
