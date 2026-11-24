"""Cipher-agnostic phrase crib (generalises blake_wordlength_crib.py). Sources: the solved LP plaintext and the
bodies of Cicada's PGP-signed messages (2012-2014 from the solver archive, the 2014 LP-image OutGuess messages,
the verified 2017 message). Every run of k consecutive words (k = 4..10, not crossing a sentence/line) is slid
along the unsolved word-length sequence (lengths in runes; TH/NG/ING one rune, EA/EO/IA/IO/OE/AE one or two).
A quotation would match exactly. Null: the same search over the unsolved word lengths in shuffled order."""
import os, re, json, glob, random, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ON = sys.argv[1] if len(sys.argv) > 1 else None   # path to a clone of the solver archive (optional)
d = json.load(open(os.path.join(ROOT, 'liber-primus__explorer', 'data', 'lp.json')))
words, where, cur = [], [], None
for p in d['pages']:
    for l in p['lines']:
        if not 7 <= l['s'] <= 15: continue
        for t in l['t']:
            if t[0] == 'r':
                if cur is None: cur = []; words.append(cur); where.append(p['page'])
                cur.append(t[1])
            else: cur = None
WL = np.array([len(w) for w in words])
def rl(word):
    w = re.sub('[^A-Z]', '', word.upper()).replace('ING', '#').replace('TH', '#').replace('NG', '#').replace('QU', 'CW')
    o = len(re.findall('EA|EO|OE|AE|IA|IO', w)); return frozenset(range(len(w) - o, len(w) + 1))
sentences = []
def add(text, src):
    for s in re.split(r'[.;:!?\n]+', text):
        ws = [w for w in re.findall(r"[A-Za-z']+", s) if re.sub('[^A-Za-z]', '', w)]
        if len(ws) >= 4 and not re.search(r'\d', s): sentences.append((src, ws))
tr = open(os.path.join(ROOT, 'liber-primus__translation', 'liber-primus__translation.txt')).read()
add('\n'.join(re.sub(r'^\S+\s+', '', l) for l in tr.splitlines() if re.match(r'^\d+\.\d+', l)), 'LP solved')
def pgp_bodies(t):
    for m in re.finditer(r'BEGIN PGP SIGNED MESSAGE-----\s*Hash: \S+\s*(.*?)-----BEGIN PGP SIGNATURE', t, re.S):
        yield '\n'.join(l for l in m.group(1).splitlines() if not re.fullmatch(r'[0-9a-fA-F ]{20,}|[A-Za-z0-9+/=]{40,}', l.strip()))
for f in sorted(glob.glob(os.path.join(ROOT, 'lp_outguessed', '*.txt'))):
    for b in pgp_bodies(open(f, errors='ignore').read()): add(b, 'signed 2014 ' + os.path.basename(f))
if ON:
    for f in sorted(glob.glob(os.path.join(ON, '**', '*.*'), recursive=True)):
        if f.endswith(('.md', '.txt', '.html')):
            for b in pgp_bodies(open(f, errors='ignore').read()): add(b, 'signed ' + os.path.relpath(f, ON)[:40])
add('Beware false paths. Always verify PGP signature from 7A35090F.', 'signed 2017')
uniq = {}
for src, ws in sentences: uniq.setdefault(tuple(w.upper() for w in ws), src)
windows = {}
for ws, src in uniq.items():
    for k in range(4, 11):
        for i in range(len(ws) - k + 1): windows.setdefault(ws[i:i + k], src)
print(len(uniq), 'distinct sentences;', len(windows), 'distinct word windows (k=4..10)')
def search(wl):
    hits = []
    for ws, src in windows.items():
        L = [rl(w) for w in ws]; k = len(L)
        ok = np.ones(len(wl) - k + 1, bool)
        for j in range(k): ok &= np.isin(wl[j:len(wl) - k + 1 + j], list(L[j]))
        hits += [(k, ws, src, i) for i in np.nonzero(ok)[0]]
    return hits
real = search(WL)
rng = np.random.default_rng(11); nulls = [search(rng.permutation(WL)) for _ in range(20)]
for k in range(4, 11):
    r = sum(h[0] == k for h in real); nl = np.array([sum(h[0] == k for h in n) for n in nulls])
    print(f'k={k:2d} words: real {r:5d} | shuffled mean {nl.mean():8.1f} sd {nl.std():6.1f}  z {(r - nl.mean()) / max(nl.std(), .5):5.2f}')
print('\nlongest real matches:')
for k, ws, src, i in sorted(real, key=lambda h: -h[0])[:12]:
    print(f'  {k} words at unsolved word {i} (page {where[i]}): {" ".join(ws)}   [{src}]')
