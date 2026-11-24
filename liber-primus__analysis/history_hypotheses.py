"""Tests suggested by the Cicada history review (history/history_insights.md), each through the full model
(autokey removed; inner layer that keeps 0 fixed: add28/sub28/mul29/imul29; key advances on every rune or skips
zeros; restart none/segment; offsets 0-9) and scored by IoC and the structure score, with matched random-key
controls (same length and value range).
 1 long keys under the skip rule: solved plaintext as running key (and reversed)
 2 pads / mp3s with Cicada's 'Skip' (every k-th byte, k=1..8) and as base-29 numbers in 8/16/32-byte chunks
 3 Valete P.S. 131-digit number: decimal digits, base-29 digits, AES(sha256)
 4 prime / totient streams anchored at the 174th (1033), 464th (3301) prime and at 1031/1229/1259, forward and backward
 5 multiplicative autokey in discrete-log space (log base 2 mod 29)
 6 hidden cicada PNG: pixel stream (row/column major) and base64 indices
 + column IoC for periods 41-200 on the non-zero steps (beyond the earlier 40 limit)"""
import os, sys, io, re, base64, hashlib, zlib
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
__file__ = os.path.join(HERE, 'retest_all.py')
exec(open(__file__).read().split("if __name__ == '__main__':")[0])       # C, D, NZ, SEG, score(), PRIMES, ...
INV = np.array([0] + [pow(x, -1, 29) for x in range(1, 29)])
SCR = '/tmp/claude-0/-home-user-iddqd/c4d0f226-87a8-5085-be90-4aec3e9a339e/scratchpad'
def ioc28(x):
    cnt = np.bincount(x, minlength=28); n = cnt.sum(); return (cnt * (cnt - 1)).sum() / (n * (n - 1)) * 28
SEGD = SEG[1:]
def peel(K, op, skip, offset, restart):
    s = D; nz = s != 0
    step = nz.astype(int) if skip else np.ones(len(s), int); idx = np.cumsum(step) - step
    if restart:
        starts = np.r_[0, np.nonzero(SEGD[1:] != SEGD[:-1])[0] + 1]; base = np.zeros(len(s), int)
        for a, b in zip(starts, list(starts[1:]) + [len(s)]): base[a:b] = idx[a]
        idx = idx - base
    k = K[(idx + offset) % len(K)]; sv, kv = s[nz], k[nz]
    if op == 'add28': return ((sv - 1) - kv) % 28
    if op == 'sub28': return ((sv - 1) + kv) % 28
    if op == 'mul29': return sv * INV[kv % 28 + 1] % 29 - 1
    return sv * (kv % 28 + 1) % 29 - 1
def evaluate(K):
    bi = bs = -9
    for op in ('add28', 'sub28', 'mul29', 'imul29'):
        for skip in (False, True):
            for rs in (False, True):
                for o in range(10):
                    x = peel(K, op, skip, o, rs)
                    bi = max(bi, ioc28(x)); bs = max(bs, score(x, 28)[0])
    return bi, bs
# ---------------- key sources ----------------
keys = {}
import re as _re
tr = open(os.path.join(HERE, '..', 'liber-primus__translation', 'liber-primus__translation.txt'), encoding='utf-8').read()
LATS = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
table = sorted([(l, i) for i, l in enumerate(LATS)] + [("K", 5), ("V", 1), ("Q", 5), ("Z", 15), ("IO", 27), ("ING", 21)], key=lambda t: -len(t[0]))
def to_runes(text):
    out = []
    for w in _re.findall('[A-Z]+', text.upper()):
        i = 0
        while i < len(w):
            m = next(((s_, v) for s_, v in table if w.startswith(s_, i)), None)
            if m: out.append(m[1]); i += len(m[0])
            else: i += 1
    return out
body = " ".join(l.split("\t")[-1] for l in tr.splitlines() if _re.match(r"\s*0\.\d+\.\d+\.\d+", l))
SP = np.array(to_runes(body))
keys['1 solved plaintext'] = SP; keys['1 solved plaintext reversed'] = SP[::-1]
def readb(p, start=0): return np.frombuffer(open(p, 'rb').read(), np.uint8)[start:].astype(int)
pads = {'_560.00': readb(f'{SCR}/iso/_560.00'), '560.17': readb(f'{SCR}/iso/560.17'), '560.13@64167': readb(f'{SCR}/iso/560.13', 64167)[:4_000_000],
        '761.mp3': readb(os.path.join(HERE, '..', '2013', '02', '761.MP3')), 'Interconnectedness.mp3': readb(os.path.join(HERE, '..', '2014', '05', '3301 - Interconnectedness.mp3'))}
for nm, b in pads.items():
    for k in (1, 2, 3, 4, 5, 6, 7, 8):
        keys[f'2 {nm} skip{k} mod29'] = b[::k][:20000] % 29
    for cs in (8, 16, 32):
        digs = []
        for i in range(0, cs * 1500, cs):
            v = int.from_bytes(bytes(b[i:i + cs].astype(np.uint8)), 'big'); dd = []
            for _ in range(int(cs * 8 / 4.858)): v, r = divmod(v, 29); dd.append(r)
            digs += dd[::-1]
            if len(digs) > 20000: break
        keys[f'2 {nm} base29 chunks{cs}'] = np.array(digs[:20000])
PS = int('1041279065891998535982789873959431895640' '442510695567564373922695237268242385295908173' '9834390370374475764863415203423499357108713631')
keys['3 Valete PS decimal'] = np.array([int(c) for c in str(PS)])
v = PS; b29 = []
while v: v, r = divmod(v, 29); b29.append(r)
keys['3 Valete PS base29'] = np.array(b29[::-1])
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
keys['3 Valete PS AES(sha256)'] = np.frombuffer(Cipher(algorithms.AES(hashlib.sha256(str(PS).encode()).digest()), modes.CTR(bytes(16))).encryptor().update(bytes(20000)), np.uint8).astype(int)
for anchor_name, idx0 in (('1033 (174th)', 173), ('3301 (464th)', 463), ('1031', int(np.searchsorted(PRIMES, 1031))), ('1229', int(np.searchsorted(PRIMES, 1229))), ('1259', int(np.searchsorted(PRIMES, 1259)))):
    keys[f'4 primes from {anchor_name}'] = PRIMES[idx0:idx0 + 20000]
    keys[f'4 totient from {anchor_name}'] = PRIMES[idx0:idx0 + 20000] - 1
    back = PRIMES[:idx0 + 1][::-1]
    keys[f'4 primes backward from {anchor_name}'] = back; keys[f'4 totient backward from {anchor_name}'] = back - 1
png = Image.open(f'{SCR}/found/560_13_xor_gematria.png'); arr = np.asarray(png.convert('LA'))[..., 0].astype(int)
keys['6 cicada pixels row-major'] = arr.flatten()[:40000]; keys['6 cicada pixels column-major'] = arr.T.flatten()[:40000]
b64txt = open(f'{SCR}/found/560_13_xor_gematria.bin', 'rb').read().split(b'\n-')[0]
alpha = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
keys['6 cicada base64 indices'] = np.array([alpha.index(ch) for ch in b64txt if ch in alpha])
rng = np.random.default_rng(42)
print('%-46s %7s %7s | %s' % ('key', 'IoC', 'struct', 'control (random key of same length/range): IoC / struct'))
results = []
for name, K in keys.items():
    K = np.asarray(K); bi, bs = evaluate(K)
    R = rng.integers(K.min(), K.max() + 1, len(K)); ci, cs_ = evaluate(R)
    results.append((name, bi, bs, ci, cs_))
    print('%-46s %7.4f %7.2f | %7.4f / %5.2f' % (name, bi, bs, ci, cs_), flush=True)
allc_i = [r[3] for r in results]; allc_s = [r[4] for r in results]
print('\nacross all %d keys: real best IoC %.4f vs control best %.4f; real best struct %.2f vs control best %.2f' %
      (len(results), max(r[1] for r in results), max(allc_i), max(r[2] for r in results), max(allc_s)))
# 5: discrete-log autokey (multiplicative autokey c[i] = c[i-1] * s[i] on non-zero runes)
g = 2; LOG = {pow(g, e, 29): e for e in range(28)}
nzc = [x for x in C if x]
ls = np.array([(LOG[b] - LOG[a]) % 28 for a, b in zip(nzc, nzc[1:])])
sh = rng.permutation(nzc); lsh = np.array([(LOG[b] - LOG[a]) % 28 for a, b in zip(sh, sh[1:])])
print('\n5 discrete-log autokey: IoC %.4f, struct %.2f   | shuffled runes: IoC %.4f, struct %.2f' % (ioc28(ls), score(ls, 28)[0], ioc28(lsh), score(lsh, 28)[0]))
# extra: column IoC periods 41-200 on the non-zero steps
def colioc(x, P):
    return np.mean([ioc28(x[j::P]) for j in range(P)])
per = [(colioc(NZ, P), P) for P in range(41, 201)]
nullper = [max(colioc(rng.permutation(NZ), P) for P in range(41, 201)) for _ in range(5)]
best = max(per)
print('column IoC on non-zero steps, periods 41-200: best %.4f at period %d; shuffled best of 160 periods: %s' % (best[0], best[1], [round(v, 4) for v in nullper]))
