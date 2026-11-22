"""Rotor-style (progressive) keys: if k[i] - k[i-1] is a constant c, a ciphertext doublet happens exactly
when the plaintext difference p[i] - p[i-1] == -c. So the ciphertext difference stream d should look like the
plaintext difference stream shifted by c. Compare against English runic text (published translations)."""
import os, re, json, collections, math
HERE = os.path.dirname(os.path.abspath(__file__))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
LAT = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
table = sorted([(l, i) for i, l in enumerate(LAT)] + [("K", 5), ("V", 1), ("Q", 5), ("Z", 15), ("IO", 27), ("ING", 21)], key=lambda t: -len(t[0]))
def to_runes(text):
    out = []
    for w in re.findall("[A-Z]+", text.upper()):
        i = 0
        while i < len(w):
            m = next(((s, v) for s, v in table if w.startswith(s, i)), None)
            if m: out.append(m[1]); i += len(m[0])
            else: i += 1
    return out
tr = open(os.path.join(HERE, '..', 'liber-primus__translation', 'liber-primus__translation.txt'), encoding='utf-8').read()
body = "\n".join(l.split("\t")[-1] for l in tr.splitlines() if re.match(r"\s*0\.\d+\.\d+\.\d+", l))
P = to_runes(body)
dp = [(b - a) % 29 for a, b in zip(P, P[1:])]
h = collections.Counter(dp); n = len(dp)
print("English sample (published translations): %d runes" % len(P))
print("plaintext difference p[i]-p[i-1] mod 29, % of pairs:")
print("  ", " ".join(f"{v}:{h[v]/n*100:.1f}" for v in range(29)))
def ioc(c, n): return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * 29
print("IoC of plaintext differences (x29): %.3f   (random 1.00)" % ioc(h, n))
lo = sorted(range(29), key=lambda v: h[v])[:4]
print("rarest differences:", [(v, f"{h[v]/n*100:.2f}%") for v in lo], "-> a key stepping by -v would give that doublet rate")
# unsolved ct differences
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
IDX = {r: i for i, r in enumerate(GP)}
U = [IDX[t[1]] for p in d['pages'] for l in p['lines'] if 7 <= l['s'] <= 15 for t in l['t'] if t[0] == 'r']
du = [(b - a) % 29 for a, b in zip(U, U[1:])]; hu = collections.Counter(du); nu = len(du)
print("unsolved ct differences IoC: %.3f" % ioc(hu, nu))
# best shift c aligning English differences to ct differences
best = []
for c in range(29):
    chi = 0
    for v in range(29):
        e = nu * h[(v - c) % 29] / n
        chi += (hu[v] - e) ** 2 / max(e, 1e-9)
    best.append((chi, c))
best.sort()
print("best constant-step fit: chi2 %.0f (28 df) at c=%d;  flat-except-zero model:" % best[0], end=" ")
e0 = nu * 0.0066; er = (nu - e0) / 28
print("chi2 %.0f" % sum((hu[v] - (e0 if v == 0 else er)) ** 2 / (e0 if v == 0 else er) for v in range(29)))
