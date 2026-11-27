"""Round 1 decryption: y_i = c_i - c_{i-1}; x_i = y_i * k_i^-1 (mod 29), k_i = (i-th prime, skipping 29) mod 29.
Usage: python3 decrypt.py [ciphertext.json] [key.txt]. Compares with plaintext_runes.json if present."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from encrypt import read_key, prime_keys, flat, reshape, write, RUNES
LAT = "F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA".split()

def decrypt(clauses, key):
    c = flat(clauses); k = prime_keys(len(c), int(key['prime_offset'])); prev = int(key['iv']); z = int(key['zero_rune']); p = []
    for ci, ki in zip(c, k):
        y = (ci - prev) % 29; prev = ci
        p.append((y * pow(ki, 27, 29) + z) % 29)   # k^-1 = k^27 mod 29
    return reshape(p, clauses)

if __name__ == '__main__':
    cf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'round1', 'ciphertext.json')
    kf = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'key.txt')
    P = decrypt(json.load(open(cf))['clauses'], read_key(kf)); write(P, HERE, 'decrypted_runes')
    for cl in P[:3]: print(' '.join(''.join(LAT[r] for r in w) for w in cl))
    ref = os.path.join(HERE, 'plaintext_runes.json')
    if os.path.exists(ref):
        R = json.load(open(ref))['clauses']
        ok = R == P; nr = len(flat(R)); bad = sum(a != b for a, b in zip(flat(R), flat(P)))
        print(f'check vs plaintext_runes.json: {"EXACT MATCH" if ok else "MISMATCH"} '
              f'({len(R)} clauses, {sum(len(c) for c in R)} words, {nr} runes, {bad} rune differences)')
