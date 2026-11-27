"""Round 2 Cicada cipher (see DESIGN.md).
  spelling : LP digraph spelling (TH, NG/ING, EO, OE, AE, IA/IO, EA are single runes)
  numbers  : n = rune position 1..29 (F=1 ... EA=29), taken mod 29, so EA = 0
  key      : K = running GP sum of the solved LP plaintext ("the book"), mod 29, zero values passed over
  inner    : y_i = n_i * K_j mod 29; EA (n = 0) gives y = 0 and the key index j does not advance
  chain    : c_i = c_{i-1} + y_i mod 29, c_{-1} = 0 (ciphertext autokey, one chain, no restarts)
  breaks   : rune stream and clause breaks unchanged; inside each clause the word lengths are permuted:
             ciphertext word t gets the length of plaintext word pi(t), pi = stable argsort of K_a..K_{a+m-1}
Usage: python3 encrypt.py [plaintext.txt] [outdir]"""
import sys, os, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
GPV = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]
LAT = "F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA".split()
TABLE = sorted([(l, [i]) for i, l in enumerate(LAT)] + [("K", [5]), ("V", [1]), ("Z", [15]), ("IO", [27]), ("ING", [21]),
                                                        ("QU", [5, 7]), ("Q", [5, 7])], key=lambda t: -len(t[0]))

def spell(word):
    out, i = [], 0
    while i < len(word):
        s, v = next((s, v) for s, v in TABLE if word.startswith(s, i)); out += v; i += len(s)
    return out

def to_runes(text):
    cl = []
    for line in text.splitlines():
        ws = [spell(w) for w in re.findall('[A-Z]+', line.upper())]
        if ws: cl.append(ws)
    return cl

def book_runes():
    sys.path.insert(0, ROOT); import lp_common as L
    return [r['p'] for r in L.R if r.get('p') is not None]       # solved segments only, page order

def key_stream(offset=0):
    """K_t = running GP sum of the book mod 29, zero values passed over (they cannot multiply)."""
    s, K = 0, []
    for b in book_runes()[offset:]:
        s += GPV[b]
        if s % 29: K.append(s % 29)
    return K

def flat(cl): return [r for c in cl for w in c for r in w]

def encrypt(P, K):
    out, prev, j, rows = [], 0, 0, []
    for clause in P:
        a = j; stream = []
        for w in clause:
            for x in w:
                n = (x + 1) % 29                        # EA -> 0
                if n == 0: y = 0                        # EA: multiplied by nothing, key waits
                else: y = n * K[j] % 29; j += 1
                prev = (prev + y) % 29; stream.append((prev - 1) % 29)   # rune number prev -> index
        m = len(clause); kv = K[a:a + m]
        pi = sorted(range(m), key=lambda t: (kv[t], t))                # stable argsort
        lens = [len(clause[pi[t]]) for t in range(m)]
        it = iter(stream); out.append([[next(it) for _ in range(L)] for L in lens])
    return out

def write(cl, outdir, name):
    os.makedirs(outdir, exist_ok=True)
    json.dump({"clauses": cl}, open(os.path.join(outdir, name + '.json'), 'w'))
    with open(os.path.join(outdir, name + '.txt'), 'w') as f:
        for c in cl: f.write('-'.join(''.join(RUNES[r] for r in w) for w in c) + '.\n')

if __name__ == '__main__':
    pt = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'plaintext.txt')
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, '..', '..', 'round2')
    P = to_runes(open(pt).read()); K = key_stream(0)
    nonEA = sum(r != 28 for r in flat(P)); assert nonEA <= len(K), 'plaintext longer than the key'
    write(P, HERE, 'plaintext_runes'); C = encrypt(P, K); write(C, out, 'ciphertext')
    with open(os.path.join(HERE, 'plaintext_runes_latin.txt'), 'w') as f:
        for c in P: f.write(' '.join(''.join(LAT[r] for r in w) for w in c) + '\n')
    print(f'{len(P)} clauses, {sum(map(len, P))} words, {len(flat(P))} runes ({flat(P).count(28)} EA); key {len(K)} values -> {out}')
