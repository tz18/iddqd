"""Find apostrophe / quote marks (small ticks in the upper part of a line) between runes in the page images.
The master transcription omits them. Reports each mark with its word context (runes before/after, separators)."""
import os, json, collections
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'lp.json')))
IMG = os.path.join(HERE, '..', 'liber-primus__images--full')
LAT = dict(zip("ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ", ["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]))
marks = []
for pg in d['pages']:
    a = np.asarray(Image.open(os.path.join(IMG, pg['img'])).convert('L')) < 110
    for li, l in enumerate(pg['lines']):
        toks = l['t']
        glyph_idx = [k for k, t in enumerate(toks) if t[0] in 'rnh' and len(t) == 6]
        if len(glyph_idx) < 3: continue
        boxes = [toks[k][2:6] for k in glyph_idx]
        hs = sorted(b[3] - b[1] for b in boxes); h = hs[len(hs) // 2]
        y0 = int(np.median([b[1] for b in boxes if b[3] - b[1] < 1.6 * h])); y1 = y0 + h
        for gi in range(len(glyph_idx) - 1):
            ka, kb = glyph_idx[gi], glyph_idx[gi + 1]
            A, B = toks[ka][2:6], toks[kb][2:6]
            if A[3] - A[1] > 1.6 * h or B[3] - B[1] > 1.6 * h: continue      # drop caps
            x0, x1 = int(A[2]) + 2, int(B[0]) - 2
            if x1 - x0 < 6: continue
            reg = a[y0 - 5:y0 + int(0.5 * h), x0:x1]
            lab, n = ndimage.label(reg)
            ticks = []
            for s in ndimage.find_objects(lab):
                hh = s[0].stop - s[0].start; ww = s[1].stop - s[1].start
                if 0.18 * h <= hh <= 0.5 * h and ww <= 0.2 * h and s[0].start < 0.25 * h: ticks.append(s)
            if ticks:
                seps = ''.join(t[1] for t in toks[ka + 1:kb] if t[0] in '-.')
                marks.append(dict(page=pg['page'], img=pg['img'], line=li, seg=l['s'], n=len(ticks), before=toks[ka][1], after=toks[kb][1],
                                  seps=seps, ka=ka, kb=kb, box=(x0, y0, x1, y1)))
def word_context(m):
    toks = d['pages'][m['page']]['lines'][m['line']]['t']
    # left word: runes back to a separator; right word likewise (same line only)
    L = []; k = m['ka']
    while k >= 0 and toks[k][0] not in '-.': L.append(toks[k][1]); k -= 1
    R = []; k = m['kb']
    while k < len(toks) and toks[k][0] not in '-.': R.append(toks[k][1]); k += 1
    return ''.join(L[::-1]), ''.join(R)
groups = collections.Counter(('unsolved' if 7 <= m['seg'] <= 15 else 'solved', 'quote (2 ticks)' if m['n'] >= 2 else 'apostrophe (1 tick)', 'inside a word' if not m['seps'] else 'next to a separator') for m in marks)
for k, v in sorted(groups.items()): print(k, v)
print('\nunsolved marks inside words (left part \' right part, as runes and Latin):')
for m in marks:
    if 7 <= m['seg'] <= 15 and not m['seps']:
        Lw, Rw = word_context(m)
        print(f"  p{m['page']:2d} ({m['img']}) line {m['line']:2d}: {Lw}'{Rw}   {'-'.join(LAT.get(c,c) for c in Lw)} ' {'-'.join(LAT.get(c,c) for c in Rw)}   ticks={m['n']}")
print('\nsolved marks inside words (check against known plaintext):')
for m in marks:
    if not 7 <= m['seg'] <= 15 and not m['seps']:
        Lw, Rw = word_context(m); print(f"  p{m['page']:2d} line {m['line']:2d}: {Lw}'{Rw}  ticks={m['n']}")
json.dump(marks, open(os.path.join(HERE, 'apostrophes.json'), 'w'), ensure_ascii=False, default=int)
# full words (crossing line breaks) containing each in-word apostrophe in the unsolved text
stream = []   # (page, line, token index, rune) for unsolved runes, with word boundaries
for pg in d['pages']:
    for li, l in enumerate(pg['lines']):
        if not 7 <= l['s'] <= 15: continue
        for k, t in enumerate(l['t']):
            if t[0] in '-.': stream.append(None)
            elif t[0] == 'r': stream.append((pg['page'], li, k, t[1]))
print('\nfull words with apostrophes (unsolved):')
for m in marks:
    if not (7 <= m['seg'] <= 15) or m['seps']: continue
    i = next(n for n, s in enumerate(stream) if s and s[:3] == (m['page'], m['line'], m['ka']))
    a = i
    while a > 0 and stream[a - 1] is not None: a -= 1
    b = i + 1
    while b < len(stream) and stream[b] is not None: b += 1
    left = ''.join(s[3] for s in stream[a:i + 1]); right = ''.join(s[3] for s in stream[i + 1:b])
    print(f"  p{m['page']} {m['img']}: {left}'{right}  ({len(left)}+{len(right)} runes)  {'-'.join(LAT[c] for c in left)} ' {'-'.join(LAT[c] for c in right)}")
