"""Pages 64-66 (unsolved) carry 256 base-60 pairs (alphabet 0-9A-Za-x) = exactly 256 bytes, all 0..255 = a 2048-bit
number S. User's idea: treat S as RSA material with Cicada's public keys (primary 7A35090F, encryption subkey
671DDEB1, both RSA-4096, e=65537):
  a) as a signature: S^e mod n -> look for PKCS#1 v1.5 / DigestInfo / any structure (also byte-reversed S)
  b) as a private exponent: x^(e*S) == x mod n ?  and does it reproduce a known Cicada signature?
  c) as an RSA modulus itself: small factors, perfect power, Fermat (close primes), gcd with Cicada's moduli
  d) as an LP key through the full model."""
import os, sys, json, string, math, hashlib, base64
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
src = open(os.path.join(HERE, 'pgp_signature_key.py')).read()
exec(src[src.index('def dearmor'):src.index('key = dearmor')])
d = json.load(open(os.path.join(ROOT, 'liber-primus__explorer', 'data', 'lp.json')))
grp = []
for p in d['pages']:
    if p['page'] in (64, 65, 66):
        for l in p['lines']:
            grp += [g for g in ''.join(t[1] if t[0] in 'hn' else ' ' for t in l['t']).split() if len(g) == 2]
A = (string.digits + string.ascii_uppercase + string.ascii_lowercase)[:60]
B = bytes(A.index(a) * 60 + A.index(b) for a, b in grp); assert len(B) == 256
print('block bytes:', B[:16].hex(), '...', B[-8:].hex(), '| sha256', hashlib.sha256(B).hexdigest()[:16])
keys = {}
for tag, body in packets(dearmor(open(os.path.join(HERE, 'sources', 'pgp', 'cicada_7A35090F.asc')).read())):
    if tag in (6, 14) and body[0] == 4 and body[5] == 1:
        n, j = mpi(body, 6); e, _ = mpi(body, j)
        kid = hashlib.sha1(b'\x99' + len(body).to_bytes(2, 'big') + body).hexdigest()[-8:].upper()
        keys[('primary ' if tag == 6 else 'subkey ') + kid] = (n, e)
def describe(m, nbytes=512):
    b = m.to_bytes(nbytes, 'big')
    lead0 = len(b) - len(b.lstrip(b'\x00'))
    printable = sum(32 <= c < 127 for c in b) / len(b)
    return f'leading zero bytes {lead0}, starts {b[:6].hex()}, printable {printable:.2f}, PKCS1 {b[:2] == bytes([0, 1]) and b[2] == 255}'
for S, form in ((int.from_bytes(B, 'big'), 'big-endian'), (int.from_bytes(B, 'little'), 'little-endian')):
    print(f'\n== S {form}: {S.bit_length()} bits, odd {S % 2 == 1}')
    for name, (n, e) in keys.items():
        print(f'  [{name}] a) S^e mod n: {describe(pow(S, e, n))}')
        print(f'  [{name}] b) S as private exponent: x^(e*S)==x ? {[pow(pow(x, S, n), e, n) == x for x in (2, 3, 3301)]}')
        print(f'  [{name}]    gcd(S, n) = {math.gcd(S, n)}')
    sp = [p for p in range(2, 10 ** 6) if all(p % q for q in range(2, int(p ** .5) + 1))] if form == 'big-endian' else sp
    small = [p for p in sp if S % p == 0]
    print('  c) small factors < 1e6:', small[:20])
    R = S
    for p in small:
        while R % p == 0: R //= p
    prime = all(pow(a, R - 1, R) == 1 for a in (2, 3, 5, 7, 11)) if R > 1 else False
    print(f'     cofactor {R.bit_length()} bits, probable prime: {prime}')
    a = math.isqrt(R) + 1; hit = None
    for _ in range(200000):
        b2 = a * a - R; b = math.isqrt(b2)
        if b * b == b2: hit = (a - b, a + b); break
        a += 1
    print('     Fermat (primes within ~2^%d of each other): %s' % (R.bit_length() // 2 - 1 + 18, 'FACTORED ' + str(hit) if hit else 'no'))
    perf = [k for k in range(2, 64) if round(R ** (1 / k)) ** k == R] if R.bit_length() < 1000 else [k for k in range(2, 30) if (lambda r: r ** k == R)(int(round(math.exp(math.log(R) / k))))]
    print('     perfect power:', perf or 'no')
sys.argv = ['x']
exec(open(os.path.join(HERE, 'history_hypotheses.py')).read().split("# ---------------- key sources ----------------")[0])
rng = np.random.default_rng(3)
print('\nd) as LP key (full model, IoC / struct; random control):')
Bi = np.frombuffer(B, np.uint8).astype(int)
for name, K in (('bytes mod 29', Bi % 29), ('base-60 values mod 29 per char', np.array([A.index(c) for c in ''.join(grp)]) % 29)):
    K = np.resize(K, 20000); bi, bs = evaluate(K); ci, cs = evaluate(rng.integers(0, 29, 20000))
    print(f'   {name:32s} IoC {bi:.4f} struct {bs:.2f} | random {ci:.4f} / {cs:.2f}')
