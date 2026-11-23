"""Is the rune distribution different at word starts (and other positions in the word)?"""
import os, json, collections
from scipy.stats import chi2 as chi2dist
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
LAT = ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
words = []; cur = None; line_start_midword = []; line_start_wordstart = []
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        if not 7 <= l['s'] <= 15: continue
        first = True
        for t in l['t']:
            if t[0] in '-.': cur = None; first = False; continue
            if t[0] != 'r': cur = None; continue
            if first:
                (line_start_midword if cur is not None else line_start_wordstart).append(t[1]); first = False
            if cur is None: cur = []; words.append(cur)
            cur.append(t[1])
allr = collections.Counter(r for w in words for r in w); N = sum(allr.values())
def test(name, runes):
    c = collections.Counter(runes); n = len(runes)
    chi = sum((c.get(v, 0) - n * allr[v] / N) ** 2 / (n * allr[v] / N) for v in GP)
    dev = sorted(GP, key=lambda v: (c.get(v, 0) - n * allr[v] / N) / (n * allr[v] / N) ** .5)
    print(f'{name:32s} n={n:5d}  chi2 {chi:6.1f} on 28 df  p={chi2dist.sf(chi, 28):.2g}   '
          f'over: {[(LAT[GP.index(v)], c.get(v,0), round(n*allr[v]/N)) for v in dev[-3:][::-1]]}  under: {[(LAT[GP.index(v)], c.get(v,0), round(n*allr[v]/N)) for v in dev[:3]]}')
test('first rune of word', [w[0] for w in words])
test('second rune of word', [w[1] for w in words if len(w) > 1])
test('last rune of word', [w[-1] for w in words])
test('middle runes', [r for w in words for r in w[1:-1]])
test('one-rune words', [w[0] for w in words if len(w) == 1])
test('line start, word start', line_start_wordstart)
test('line start, mid-word', line_start_midword)
