"""Round 1 Cicada cipher: F-passthrough multiplication by the primes, under ciphertext autokey.
  x_i = plaintext rune index (0..28, F = 0)
  y_i = x_i * k_i mod 29,  k_i = (i-th prime, skipping 29) mod 29   (F -> 0 always: F is not encrypted)
  c_i = c_{i-1} + y_i mod 29,  c_{-1} = 0
Usage: python3 encrypt.py [plaintext.txt] [key.txt] [outdir]"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
LETTER = dict(F=[0], U=[1], V=[1], O=[3], R=[4], C=[5], K=[5], Q=[5, 7], G=[6], W=[7], H=[8], N=[9], I=[10], J=[11],
              P=[13], X=[14], S=[15], Z=[15], T=[16], B=[17], E=[18], M=[19], L=[20], D=[23], A=[24], Y=[26])

def read_key(path):
    k = {}
    for line in open(path):
        line = line.split('#')[0].strip()
        if '=' in line:
            a, b = line.split('='); k[a.strip()] = b.strip()
    assert k['spelling'] == 'letter' and k['key_stream'] == 'primes' and k['key_index'] == 'every_rune'
    return k

def prime_keys(n, offset=0):
    """k_i = (i-th prime) mod 29 for i = offset .. offset+n-1, counting primes 2,3,5,... but passing over 29."""
    out, m = [], 2
    while len(out) < n + offset:
        if all(m % q for q in range(2, int(m ** .5) + 1)) and m % 29:
            out.append(m % 29)
        m += 1
    return out[offset:]

def to_runes(text):
    clauses = []
    for line in text.splitlines():
        words = [[r for ch in w if ch.isalpha() for r in LETTER[ch]] for w in line.split()]
        words = [w for w in words if w]
        if words: clauses.append(words)
    return clauses

def flat(clauses): return [r for cl in clauses for w in cl for r in w]

def reshape(seq, like):
    it = iter(seq); return [[[next(it) for _ in w] for w in cl] for cl in like]

def encrypt(clauses, key):
    p = flat(clauses); k = prime_keys(len(p), int(key['prime_offset'])); prev = int(key['iv']); z = int(key['zero_rune']); c = []
    for x, ki in zip(p, k):
        y = ((x - z) * ki) % 29           # zero_rune is 0 (F): F passes through as y = 0
        prev = (prev + y) % 29; c.append(prev)
    return reshape(c, clauses)

def write(clauses, outdir, name='ciphertext'):
    os.makedirs(outdir, exist_ok=True)
    json.dump({"clauses": clauses}, open(os.path.join(outdir, name + '.json'), 'w'))
    with open(os.path.join(outdir, name + '.txt'), 'w') as f:
        for cl in clauses: f.write('-'.join(''.join(RUNES[r] for r in w) for w in cl) + '.\n')

if __name__ == '__main__':
    pt = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'plaintext.txt')
    kf = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'key.txt')
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, '..', 'round1')
    key = read_key(kf); P = to_runes(open(pt).read())
    write(P, HERE, 'plaintext_runes')                 # rune plaintext, for the decryption check
    C = encrypt(P, key); write(C, out)
    print(f'{len(P)} clauses, {sum(len(c) for c in P)} words, {len(flat(P))} runes -> {out}/ciphertext.json/.txt')
