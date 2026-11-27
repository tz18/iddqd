"""Round 2 decryption from ciphertext.json plus the key (the solved LP plaintext as a public book).
  1. y_i = c_i - c_{i-1} (rune numbers 1..29 mod 29, c_{-1} = 0)
  2. y_i = 0 -> EA (key waits); else n_i = y_i * K_j^-1 = y_i * K_j^27 mod 29, j += 1; rune index = n_i - 1
  3. per clause: a = key index at its first rune, pi = stable argsort of K_a..K_{a+m-1}; the ciphertext word t has the
     length of plaintext word pi(t), so plaintext lengths are recovered by inverting pi; the runes are re-cut.
Usage: python3 decrypt.py [ciphertext.json] [out.json]; compares with plaintext_runes.json if present."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
GPV = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]
LAT = "F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA".split()

def key_stream():
    sys.path.insert(0, ROOT); import lp_common as L
    s, K = 0, []
    for r in L.R:
        if r.get('p') is None: continue
        s += GPV[r['p']]
        if s % 29: K.append(s % 29)
    return K

def decrypt(C, K):
    prev, j, P = 0, 0, []
    for clause in C:
        a = j; runes = []
        for w in clause:
            for r in w:
                c = (r + 1) % 29; y = (c - prev) % 29; prev = c
                if y == 0: runes.append(28)
                else: runes.append((y * pow(K[j], 27, 29) - 1) % 29); j += 1
        m = len(clause); kv = K[a:a + m]; pi = sorted(range(m), key=lambda t: (kv[t], t))
        lens = [0] * m
        for t in range(m): lens[pi[t]] = len(clause[t])
        it = iter(runes); P.append([[next(it) for _ in range(L)] for L in lens])
    return P

if __name__ == '__main__':
    cf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'round2', 'ciphertext.json')
    of = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'decrypted_runes.json')
    P = decrypt(json.load(open(cf))['clauses'], key_stream())
    json.dump({"clauses": P}, open(of, 'w'))
    for c in P[:3]: print(' '.join(''.join(LAT[r] for r in w) for w in c))
    ref = os.path.join(HERE, 'plaintext_runes.json')
    if os.path.exists(ref):
        Q = json.load(open(ref))['clauses']
        fr = lambda X: [r for c in X for w in c for r in w]
        shape = lambda X: [[len(w) for w in c] for c in X]
        diff = sum(a != b for a, b in zip(fr(P), fr(Q))) + abs(len(fr(P)) - len(fr(Q)))
        print(f'check: {len(P)} clauses, {sum(map(len, P))} words, {len(fr(P))} runes; rune differences {diff}; '
              f'word/clause structure identical: {shape(P) == shape(Q)}; exact match: {P == Q}')
