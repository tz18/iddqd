"""Solve the period-13 key on pages 69-70 under: plaintext+1 (EA->F), Vigenere period 13 skipping F, ct autokey.
Each column's shift is chosen to best match English (rotated) frequencies; then print the decryption."""
import os, collections, math
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'pages_54_55.py')).read().split("pg = list(page)")[0]
exec(src)
exec(open(os.path.join(HERE, 'progressive_key.py')).read().split('dp = [')[0])   # P: English sample, LAT
eng = collections.Counter(P); tot = len(P)
for modulus in (29, 28):
    # alphabet for the Vigenere: all 29 runes, or the 28 non-F runes (so F is never produced)
    alph = list(range(29)) if modulus == 29 else list(range(1, 29))
    pos = {v: i for i, v in enumerate(alph)}
    rot = [(x + 1) % 29 for x in P]                      # rotated plaintext (EA -> F)
    fr = collections.Counter(r for r in rot if r in pos); ft = sum(fr.values())
    logp = {v: math.log((fr[v] + .5) / (ft + 15)) for v in alph}
    x = dstream([r for k in (69, 70) for _, r in page[k]])   # zeros dropped
    key = []
    for j in range(13):
        col = x[j::13]
        best = max(range(modulus), key=lambda k: sum(logp[alph[(pos[c] - k) % modulus]] for c in col if c in pos))
        key.append(best)
    plain_rot = [alph[(pos[c] - key[i % 13]) % modulus] if c in pos else c for i, c in enumerate(x)]
    plain = [(v - 1) % 29 for v in plain_rot]
    print(f'mod {modulus} key {key}')
    print('  ', ''.join(LAT[v] for v in plain[:160]))
