"""Theory (user): clauses whose GP sum is prime are 'divine' and need no decryption: they are KEYSTREAM for the rest.
Keys: (a) the unsolved prime clauses (ciphertext runes, all 31 or the 18 short), forward and reversed;
      (b) the solved LP plaintext of its prime clauses (45), forward and reversed.
Targets/schemes: (1) running key over the concatenated non-prime clauses; (2) local: each non-prime clause is
decrypted by the most recent prime clause (cycled, restarting per clause); (3) the full model
(history_hypotheses.evaluate: autokey removal, rare-rune shift, inner mod-28/mul layer, 160 settings).
Ops for (1),(2): x = c-k, c+k, k-c mod 29, with and without the 'F not encrypted, key does not advance' rule.
Score: IoC x29 (English ~1.7, random 1.0). Control for (a): the same scheme with keys made of the same number of
randomly chosen NON-prime clauses (200 draws): z and p. For (b): random runes of the same length as control."""
import os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import R, UNS, VAL, d, PR
isp = set(PR); V = np.array(VAL); rng = np.random.default_rng(33)
cl = collections.OrderedDict()
for r in UNS: cl.setdefault(r['clause'], []).append(r['c'])
CL = [np.array(v) for v in cl.values()]
prime = np.array([V[c].sum() in isp for c in CL]); short = np.array([len(c) <= 31 for c in CL])
NP = [c for c, p in zip(CL, prime) if not p]; T = np.concatenate(NP)
sol = collections.OrderedDict()
for r in R:
    if d['segments'][r['seg']]['solved']: sol.setdefault(r['clause'], []).append(r['p'])
SOLP = np.concatenate([np.array(v) for v in sol.values() if V[v].sum() in isp])
def ioc(x):
    c = np.bincount(x, minlength=29); n = c.sum(); return (c * (c - 1)).sum() / (n * (n - 1)) * 29
def apply(c, k, op, fskip):
    out = []; j = 0
    for x in c:
        if fskip and x == 0: out.append(0); continue
        kk = k[j % len(k)]; j += 1
        out.append((x - kk) % 29 if op == 0 else (x + kk) % 29 if op == 1 else (kk - x) % 29)
    return np.array(out)
def running(K):
    return max(ioc(apply(T, K, op, fs)) for op in range(3) for fs in (0, 1))
def local(keyclauses_mask):
    best = 0
    for op in range(3):
        for fs in (0, 1):
            outs = []; cur = None
            for c, km in zip(CL, keyclauses_mask):
                if km: cur = c; continue
                if cur is not None: outs.append(apply(c, cur, op, fs))
            best = max(best, ioc(np.concatenate(outs)))
    return best
def report(name, real, nulls):
    nulls = np.array(nulls); print(f'{name:58s} IoC {real:.4f} | control {nulls.mean():.4f} +/- {nulls.std():.4f}  z {(real - nulls.mean()) / nulls.std():5.2f}  p {np.mean(nulls >= real):.3f}', flush=True)
idx_np = np.nonzero(~prime)[0]
for lab, mask in (('all 31 prime clauses', prime), ('18 short prime clauses', prime & short)):
    K = np.concatenate([c for c, m in zip(CL, mask) if m]); m = mask.sum()
    def rand_mask():
        mm = np.zeros(len(CL), bool); mm[rng.choice(idx_np, m, replace=False)] = True; return mm
    ctrl_keys = [np.concatenate([c for c, mm in zip(CL, rand_mask()) if mm]) for _ in range(200)]
    report(f'(1) running key = {lab}', running(K), [running(k) for k in ctrl_keys])
    report(f'(1) running key = {lab}, reversed', running(K[::-1]), [running(k[::-1]) for k in ctrl_keys])
    report(f'(2) local: each prime clause decrypts what follows ({lab})', local(mask), [local(rand_mask()) for _ in range(200)])
report('(1) running key = solved LP prime-clause plaintext', running(SOLP), [running(rng.integers(0, 29, len(SOLP))) for _ in range(200)])
report('(1) running key = solved LP prime-clause plaintext, reversed', running(SOLP[::-1]), [running(rng.integers(0, 29, len(SOLP))) for _ in range(200)])
# (3) full model with these keys over the whole unsolved stream
sys.argv = ['x']
exec(open(os.path.join(HERE, 'history_hypotheses.py')).read().split("# ---------------- key sources ----------------")[0])
print('\n(3) full model (best of 160 settings), IoC / structure; control = random runes of the same length')
for lab, K in (('unsolved prime clauses', np.concatenate([c for c, p in zip(CL, prime) if p])),
               ('solved LP prime-clause plaintext', SOLP)):
    for rev in (False, True):
        KK = K[::-1] if rev else K; bi, bs = evaluate(np.resize(KK, 20000))
        cs = [evaluate(np.resize(rng.integers(0, 29, len(K)), 20000)) for _ in range(5)]
        print(f'   {lab}{" reversed" if rev else "":10s} IoC {bi:.4f} struct {bs:.2f} | controls IoC max {max(c[0] for c in cs):.4f} struct max {max(c[1] for c in cs):.2f}', flush=True)
# (4) the prime NUMBER as key: the sum S of each prime clause keys the clauses after it, until the next prime clause.
#   shift by S mod 29; multiply by S mod 29 (S is never a multiple of 29); key = decimal digits of S (cycled); key =
#   base-29 digits of S. Control: the same with the sums of randomly chosen non-prime clauses as the 'key clauses'.
def digits(S, b):
    out = []
    while S: S, r = divmod(S, b); out.append(r)
    return out[::-1]
INV = [0] + [pow(i, -1, 29) for i in range(1, 29)]
def numkey(mask, mode):
    best = 0
    for op in range(3):
        outs = []; S = None
        for c, km in zip(CL, mask):
            if km: S = int(V[c].sum()); continue
            if S is None: continue
            if mode == 'mul': outs.append(np.array([x * INV[S % 29] % 29 if op == 0 else x * (S % 29) % 29 for x in c])); continue
            k = [S % 29] if mode == 'shift' else digits(S, 10 if mode == 'dec' else 29)
            outs.append(apply(c, np.array(k), op, 0))
        best = max(best, ioc(np.concatenate(outs)))
    return best
print('\n(4) prime sum S as the key for the following clauses')
m = prime.sum()
def rand_mask():
    mm = np.zeros(len(CL), bool); mm[rng.choice(idx_np, m, replace=False)] = True; return mm
for mode in ('shift', 'mul', 'dec', 'b29'):
    report(f'   S -> {mode}', numkey(prime, mode), [numkey(rand_mask(), mode) for _ in range(200)])
