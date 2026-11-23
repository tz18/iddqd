"""Period-13 key with occasional skips (key does not advance), on the autokey-removed stream of pages 68-70.
Hidden state = key phase 0..12. At each position the phase advances by 1, or stays (a skip: the rune passes
unencrypted and the key does not advance) with a penalty. Plaintext p = d - key[phase] (mod 29), scored by English
rune unigram log-probabilities (skipped runes scored as plaintext d itself).
Fit: Viterbi path for the current key, re-estimate each phase's key value from the runes on that phase; iterate.
Same fit on shuffled copies (doublet count kept) is the control. Score: IoC of the decryption, and log-likelihood."""
import os, json, random, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
LAT = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
exec(open(os.path.join(HERE, 'progressive_key.py')).read().split('dp = [')[0])
eng = collections.Counter(P); LOGP = np.log((np.array([eng[v] for v in range(29)]) + .5) / (len(P) + 14.5))
PER = 13
def fit(c, skip_pen=4.0, iters=12, restarts=6, rng=None):
    c = np.array(c); dd = (c[1:] - c[:-1]) % 29; n = len(dd)
    best = (-1e18, None, None)
    for r in range(restarts):
        key = (rng.integers(0, 29, PER) if rng is not None else np.random.default_rng(r).integers(0, 29, PER))
        for _ in range(iters):
            # Viterbi over phases: emission for advancing at phase f: LOGP[(d - key[f])], for skip: LOGP[d] - pen
            V = np.full(PER, -1e18); V[:] = 0; back = np.zeros((n, PER), int); skipflag = np.zeros((n, PER), bool)
            for i in range(n):
                emit = LOGP[(dd[i] - key) % 29]               # using phase f at position i
                adv = np.roll(V, 1) + emit                     # came from phase f-1, advanced
                stay = V + LOGP[dd[i]] - skip_pen              # skip: phase unchanged, rune unencrypted
                choose_adv = adv >= stay
                newV = np.where(choose_adv, adv, stay)
                back[i] = np.where(choose_adv, (np.arange(PER) - 1) % PER, np.arange(PER)); skipflag[i] = ~choose_adv
                V = newV
            f = int(np.argmax(V)); ll = float(V[f]); path = np.zeros(n, int); skips = np.zeros(n, bool)
            for i in range(n - 1, -1, -1):
                path[i] = f; skips[i] = skipflag[i, f]; f = back[i, f]
            # re-estimate key per phase from non-skipped runes
            newkey = key.copy()
            for ph in range(PER):
                xs = dd[(path == ph) & ~skips]
                if len(xs): newkey[ph] = max(range(29), key=lambda k: LOGP[(xs - k) % 29].sum())
            if np.array_equal(newkey, key): break
            key = newkey
        if ll > best[0]: best = (ll, key.copy(), (path, skips))
    ll, key, (path, skips) = best
    pt = np.where(skips, dd, (dd - key[path]) % 29)
    cnt = np.bincount(pt, minlength=29); ioc = (cnt * (cnt - 1)).sum() / (len(pt) * (len(pt) - 1)) * 29
    return ll / n, ioc, key, int(skips.sum()), pt
seq = [IDX[t[1]] for p in d['pages'] if p['page'] in (68, 69, 70) for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
ll, ioc, key, nsk, pt = fit(seq)
print(f'pages 68-70 ({len(seq)} runes): log-lik/rune {ll:.3f}, IoC of decryption {ioc:.3f}, skips {nsk}, key {"".join(GP[k] for k in key)} ({"-".join(LAT[k] for k in key)})')
print('decryption:', ''.join(LAT[x] for x in pt[:150]))
rng = random.Random(4); nrng = np.random.default_rng(4)
def shuffle_keep_doublets(s):
    a = s[:]; target = sum(x == y for x, y in zip(s, s[1:]))
    for _ in range(2000):
        rng.shuffle(a)
        if sum(x == y for x, y in zip(a, a[1:])) == target: return a
    return a
ctrl = [fit(shuffle_keep_doublets(seq), rng=nrng)[:2] for _ in range(20)]
cl = np.array([x[0] for x in ctrl]); ci = np.array([x[1] for x in ctrl])
print(f'control (20 shuffles): log-lik/rune median {np.median(cl):.3f} max {cl.max():.3f}; IoC median {np.median(ci):.3f} max {ci.max():.3f}')
print('English text scores about %.3f log-lik/rune and IoC ~1.73' % (LOGP[np.array(P)].mean()))
