"""Follow-up on DJU BEI: positions within segments, and whether whole words repeat more than chance."""
import os, json, collections, random
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
LAT = dict(zip(GP, ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]))
words = []   # (word string, seg, rune pos in seg, page, line)
segpos = collections.Counter(); cur = None
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        if not 7 <= l['s'] <= 15: continue
        for t in l['t']:
            if t[0] in '-.': cur = None; continue
            if t[0] != 'r': cur = None; continue
            if cur is None:
                cur = [t[1], l['s'], segpos[l['s']], p['page'], li]; words.append(cur)
            else: cur[0] += t[1]
            segpos[l['s']] += 1
for i, w in enumerate(words):
    if w[0] == 'ᛞᛄᚢ' and i + 1 < len(words) and words[i + 1][0] == 'ᛒᛖᛁ':
        print(f'DJU BEI: segment {w[1]}, rune {w[2]} of {segpos[w[1]]} in segment, word #{i}, page {w[3]} line {w[4]}')
cnt = collections.Counter(w[0] for w in words)
def rep_stats(ws, minlen):
    c = collections.Counter(w for w in ws if len(w) >= minlen)
    return sum(v - 1 for v in c.values() if v > 1)
rng = random.Random(9)
flat = [r for w in words for r in w[0]]; lens = [len(w[0]) for w in words]
print('\nrepeated whole words (extra copies), real vs runes shuffled between words (same word lengths):')
for ml in (3, 4, 5):
    real = rep_stats([w[0] for w in words], ml)
    null = []
    for _ in range(200):
        f = flat[:]; rng.shuffle(f); i = 0; ws = []
        for L in lens: ws.append(''.join(f[i:i + L])); i += L
        null.append(rep_stats(ws, ml))
    m = sum(null) / len(null); sd = (sum((x - m) ** 2 for x in null) / len(null)) ** .5
    print(f'  length >= {ml}: real {real}   shuffled {m:.1f} ± {sd:.1f}   p(>=real) = {sum(x >= real for x in null) / len(null):.3f}')
print('\nrepeated words of length >= 4:', [(w, '-'.join(LAT[c] for c in w), n) for w, n in cnt.most_common() if n > 1 and len(w) >= 4])
# repeated adjacent word PAIRS (like DJU BEI)
pairs = collections.Counter((words[i][0], words[i + 1][0]) for i in range(len(words) - 1) if words[i][1] == words[i + 1][1])
print('repeated adjacent word pairs:', [(a + ' ' + b, n) for (a, b), n in pairs.items() if n > 1])
