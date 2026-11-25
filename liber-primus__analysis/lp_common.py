"""Shared loader: runes with page/line/word/clause/segment, plus plaintext for solved segments
(same default ciphers and F-skips as the workbench: atbash, atbash+3, Vigenere DIVINITY / FIRFUMFERENFE, totient)."""
import os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
GP = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"; IDX = {r: i for i, r in enumerate(GP)}
VAL = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
def _primes(n):
    s = bytearray([1]) * (n + 1); s[0:2] = b'\0\0'
    for i in range(2, int(n ** .5) + 1):
        if s[i]: s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]
PR = _primes(200000)
R = []   # dict per rune
word = clause = 0
for p in d['pages']:
    for li, l in enumerate(p['lines']):
        col = 0
        for t in l['t']:
            if t[0] == 'r':
                R.append(dict(c=IDX[t[1]], page=p['page'], line=li, col=col, word=word, clause=clause, seg=l['s'], para=l['p'],
                              box=t[2:6] if len(t) == 6 else None)); col += 1
            elif t[0] == '-': word += 1
            elif t[0] == '.': word += 1; clause += 1
            else: word += 1
        # line break does not end a word
    clause += 0
# plaintext for solved segments
cfg = {s['name']: s for s in d['segments']}
for si, s in enumerate(d['segments']):
    cph = s['cipher']; idx = [i for i, r in enumerate(R) if r['seg'] == si]
    skips = set(cph.get('skips', [])); j = 0
    for pos, i in enumerate(idx):
        c = R[i]['c']
        if not s['solved']: R[i]['p'] = None; continue
        if pos in skips: R[i]['p'] = c; continue
        x = (28 - c + cph.get('shift', 0)) if cph['type'] == 'atbash' else c
        k = cph['key'][j % len(cph['key'])] if cph['type'] == 'vigenere' else (PR[j] - 1 if cph['type'] == 'totient' else 0)
        R[i]['p'] = (x - k) % 29; j += 1
UNS = [r for r in R if 7 <= r['seg'] <= 15]
LAT = "F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA".split()
