"""Follow-up on the period-13 signal on pages 69-70 (unsolved-folder 54-55).
(1) FIRFUMFERENFE (Koan 2 key) at every offset on raw and autokey-removed text, +/-, with/without the F-skip.
(2) frequency-solve 13 column shifts on the autokey-removed stream (zeros kept) and print the decryption.
(3) where does the signal come from: column IoC with page 69 and page 70 separately, and with DJU BEI removed."""
import os, json, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
LAT = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
seq = [IDX[t[1]] for p in d['pages'] if p['page'] in (69, 70) for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
c = np.array(seq); dd = (c[1:] - c[:-1]) % 29
def ioc(x):
    cnt = np.bincount(np.asarray(x) % 29, minlength=29); n = cnt.sum(); return (cnt * (cnt - 1)).sum() / (n * (n - 1)) * 29
FIR = [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18]
res = []
for tname, T in (('raw', c), ('autokey removed', dd)):
    for op in (1, -1):
        for skipF in (False, True):
            for off in range(13):
                out = []; j = off
                for x in T:
                    if skipF and x == 0: out.append(0); continue
                    out.append((x - op * FIR[j % 13]) % 29); j += 1
                res.append((ioc(out), tname, op, skipF, off, out))
res.sort(key=lambda r: -r[0])
print('(1) FIRFUMFERENFE on pages 69-70: best IoC %.3f (%s, %s, F-skip %s, offset %d); English ~1.73' % (res[0][0], res[0][1], 'subtract' if res[0][2] > 0 else 'add', res[0][3], res[0][4]))
print('    decryption:', ''.join(LAT[x] for x in res[0][5][:80]))
# (2) frequency solve on autokey-removed stream, zeros kept
exec(open(os.path.join(HERE, 'progressive_key.py')).read().split('dp = [')[0])  # P english runes
eng = collections.Counter(P); tot = len(P)
for shiftsign in (1,):
    logp = np.log((np.array([eng[v] for v in range(29)]) + .5) / (tot + 15))
    for rot in (0,):
        key = []
        for j in range(13):
            col = dd[j::13]
            key.append(max(range(29), key=lambda k: sum(logp[(x - k) % 29] for x in col)))
        pt = [(x - key[i % 13]) % 29 for i, x in enumerate(dd)]
        print('(2) frequency-solved key:', key, ''.join(GP[k] for k in key), '-'.join(LAT[k] for k in key))
        print('    decryption:', ''.join(LAT[x] for x in pt[:120]))
        print('    IoC of decryption %.3f' % ioc(pt))
# (3) where is the signal
def colp(x, per=13):
    t = 0
    for j in range(per):
        cc = np.bincount(x[j::per], minlength=29); k = cc.sum(); t += (cc * (cc - 1)).sum() / (k * (k - 1)) * 29 if k > 1 else 0
    return t / per
p69 = [IDX[t[1]] for p in d['pages'] if p['page'] == 69 for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
print('(3) column IoC at 13: page 69 only %.3f (%d runes); pages 69-70 %.3f; pages 69-70 minus the final DJU BEI %.3f' % (
    colp((np.array(p69[1:]) - np.array(p69[:-1])) % 29), len(p69), colp(dd), colp(dd[:-6])))
# which columns carry it
cols = [(round(ioc(dd[j::13]), 2), int(len(dd[j::13]))) for j in range(13)]
print('    per-column IoC (n):', cols)
