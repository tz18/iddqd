"""The 2017-04-04 'Beware false paths' signature, treated as data (user's idea):
1. RSA-verify it with Cicada's public key 7A35090F (keyserver.ubuntu.com): s^e mod n should be PKCS#1 v1.5
   padding + SHA-512 DigestInfo + hash of the clearsigned text. If that holds, the 512 bytes are fully explained
   by the signing process and carry nothing hidden.
2. 'Sign with it as a private key': is d = s a valid private exponent for Cicada's modulus, i.e. x^(e*s) = x?
   Also s^d style checks are impossible without d; report.
3. Use the signature integer as an LP keystream (bytes mod 29, base-29 digits) through the full model."""
import os, sys, base64, hashlib, re
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, 'sources', 'pgp')
def dearmor(txt):
    body = [l for l in txt.splitlines() if l and not l.startswith(('-----', 'Version', 'Comment', '=')) and ':' not in l]
    return base64.b64decode(''.join(body))
def packets(b):
    i = 0
    while i < len(b):
        h = b[i]; assert h & 0x80
        if h & 0x40:   # new format
            tag = h & 0x3f; l = b[i + 1]
            if l < 192: hl, ln = 2, l
            elif l < 224: hl, ln = 3, ((l - 192) << 8) + b[i + 2] + 192
            else: hl, ln = 6, int.from_bytes(b[i + 2:i + 6], 'big')
        else:
            tag = (h >> 2) & 0xf; lt = h & 3; n = [1, 2, 4][lt]; hl = 1 + n; ln = int.from_bytes(b[i + 1:i + 1 + n], 'big')
        yield tag, b[i + hl:i + hl + ln]; i += hl + ln
def mpi(b, i):
    bits = int.from_bytes(b[i:i + 2], 'big'); n = (bits + 7) // 8
    return int.from_bytes(b[i + 2:i + 2 + n], 'big'), i + 2 + n
key = dearmor(open(os.path.join(P, 'cicada_7A35090F.asc')).read())
tag, pk = next(packets(key)); assert tag == 6 and pk[0] == 4 and pk[5] == 1
n, j = mpi(pk, 6); e, _ = mpi(pk, j)
fp = hashlib.sha1(b'\x99' + len(pk).to_bytes(2, 'big') + pk).hexdigest().upper()
print('Cicada key fingerprint', fp, '| RSA', n.bit_length(), 'bits, e =', e)
sig = base64.b64decode(open(os.path.join(P, '2017-04-04_beware_false_paths.sig.b64')).read().replace(' ', '').replace('\n', ''))
tag, sp = next(packets(sig)); assert tag == 2
ver, stype, palg, halg = sp[0:4]; hl = int.from_bytes(sp[4:6], 'big'); hashed = sp[6:6 + hl]
ul = int.from_bytes(sp[6 + hl:8 + hl], 'big'); k = 8 + hl + ul; left16 = sp[k:k + 2]; s, _ = mpi(sp, k + 2)
print(f'sig v{ver} type {stype:#x} (text) pubalg {palg} hash {halg} (SHA-512); s has {s.bit_length()} bits; hash prefix {left16.hex()}')
m = pow(s, e, n); em = m.to_bytes(512, 'big')
DI = bytes.fromhex('3051300d060960864801650304020305000440')
ok_pad = em.startswith(b'\x00\x01') and em[2:em.index(b'\x00', 2)] == b'\xff' * (em.index(b'\x00', 2) - 2)
rest = em[em.index(b'\x00', 2) + 1:]
print('s^e mod n is PKCS#1 v1.5 padding:', ok_pad, '| SHA-512 DigestInfo:', rest[:19] == DI)
digest = rest[19:]
print('  signed hash:', digest.hex()[:32] + '...', '| matches prefix', digest[:2] == left16)
trailer = sp[:6 + hl] + b'\x04\xff' + (6 + hl).to_bytes(4, 'big')
found = None
for variant in ['Beware false paths.  Always verify PGP signature from 7A35090F.\n\n3301\n']:   # exact layout found by trying line-break variants
    t = '\r\n'.join(l.rstrip() for l in variant.split('\n')).encode()
    if hashlib.sha512(t + trailer).digest() == digest: found = variant; break
print('  message text reproduces the hash:', repr(found) if found else 'no (whitespace variant not found)')
print('\n2. s as a private exponent: x^(e*s) == x mod n ?', [pow(pow(x, s, n), e, n) == x for x in (2, 3, 3301)])
print('   gcd(s, n) =', __import__('math').gcd(s, n), '(1 = shares no factor with the modulus)')
# 3. as an LP key
sys.argv = ['x']
exec(open(os.path.join(HERE, 'history_hypotheses.py')).read().split("# ---------------- key sources ----------------")[0])
import numpy as np
sb = np.frombuffer(s.to_bytes(512, 'big'), np.uint8).astype(int)
d29 = []; x = s
while x: x, r = divmod(x, 29); d29.append(r)
rng = np.random.default_rng(7)
print('\n3. signature as LP key (full model: IoC, struct; random control):')
for name, K in (('bytes mod 29', sb % 29), ('base-29 digits', np.array(d29[::-1])), ('whole sig packet bytes mod 29', np.frombuffer(sig, np.uint8).astype(int) % 29)):
    K = np.resize(K, 20000); bi, bs = evaluate(K); ci, cs = evaluate(rng.integers(0, 29, 20000))
    print(f'   {name:30s} IoC {bi:.4f} struct {bs:.2f} | random {ci:.4f} / {cs:.2f}')
