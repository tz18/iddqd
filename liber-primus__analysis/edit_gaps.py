"""Ink gap between consecutive runes inside a word (next.x0 - cur.x1), in pixels, for exactly-matched lines.
A glyph swapped for one of a different width without re-laying the line leaves an irregular gap.
Compare gap regularity: unsolved vs solved, and LP2 unsolved vs LP2 solved (pages 71-72 = images 73-74)."""
import os, json, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'layout.json')))
gaps = collections.defaultdict(list); heights = collections.defaultdict(list)
for pg in L:
    for l in pg['lines']:
        if l['flag'] != 'ok': continue
        boxes = iter(l['boxes']); prev = None
        for it in l['items']:
            if it[0] == 'sep': prev = None; continue
            b = next(boxes)
            if it[0] != 'rune' or not b: prev = None; continue
            if prev is not None and (b[3] - b[1]) < 200 and (prev[3] - prev[1]) < 200:
                group = 'unsolved' if 7 <= l['seg'] <= 15 else ('LP2 solved' if pg['page'] >= 71 else 'LP1 solved')
                gaps[group].append(b[0] - prev[2]); heights[group].append(b[3] - b[1])
            prev = b
for g in ('unsolved', 'LP1 solved', 'LP2 solved'):
    x = np.array(gaps[g]); h = np.median(heights[g])
    med = np.median(x)
    print(f'{g:11s} n={len(x):5d}  glyph height {h:.0f}px  gap median {med:.0f}px  '
          f'IQR {np.percentile(x,25):.0f}-{np.percentile(x,75):.0f}px  '
          f'|gap-median|>8px: {np.mean(np.abs(x-med)>8):.2%}  >15px: {np.mean(np.abs(x-med)>15):.2%}  >25px: {np.mean(np.abs(x-med)>25):.2%}')
    print('             gap histogram (px):', dict(sorted(collections.Counter(int(v) for v in x if -10 <= v <= 40).items())))
