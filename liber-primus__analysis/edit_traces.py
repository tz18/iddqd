"""Look for traces of manual edits in the page images: per-rune outliers in spacing (advance to the next rune
within a word), vertical alignment, width, and glyph shape (pixel difference from the median image of that rune).
Only lines the segmenter matched glyph-for-glyph are used. Compare outlier rates on unsolved vs solved pages."""
import os, json, collections
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, '..', 'liber-primus__explorer', 'data', 'layout.json')))
IMG = os.path.join(HERE, '..', 'liber-primus__images--full')
recs = []   # one per rune
for pg in L:
    im = np.asarray(Image.open(os.path.join(IMG, pg['image'])).convert('L')).astype(np.float32) / 255
    rgb = None
    for li, l in enumerate(pg['lines']):
        if l['flag'] != 'ok': continue
        items = [it for it in l['items'] if it[0] in ('rune', 'sep', 'num', 'hex')]
        boxes = iter(l['boxes']); glyphs = []
        for it in items:
            if it[0] == 'sep': glyphs.append(('sep', it[1], None)); continue
            glyphs.append((it[0], it[1], next(boxes)))
        rb = [g for g in glyphs if g[0] == 'rune' and g[2]]
        if len(rb) < 5: continue
        hs = sorted(b[3] - b[1] for _, _, b in rb); h = hs[len(hs) // 2]
        y0m = np.median([b[1] for _, _, b in rb]); y1m = np.median([b[3] for _, _, b in rb])
        for k, (kind, ch, b) in enumerate(glyphs):
            if kind != 'rune' or not b or (b[3] - b[1]) > 1.6 * h: continue          # skip drop caps
            nxt = glyphs[k + 1] if k + 1 < len(glyphs) else None
            adv = (nxt[2][0] - b[0]) / h if nxt and nxt[0] == 'rune' and nxt[2] else None
            crop = im[int(b[1]):int(b[3]), int(b[0]):int(b[2])]
            if crop.size == 0: continue
            patch = np.asarray(Image.fromarray((crop * 255).astype(np.uint8)).resize((16, 32))).astype(np.float32) / 255
            recs.append(dict(page=pg['page'], seg=l['seg'], ch=ch, nxt=nxt[1] if adv is not None else None, adv=adv,
                             w=(b[2] - b[0]) / h, top=(b[1] - y0m) / h, bot=(b[3] - y1m) / h, patch=patch))
print('runes measured:', len(recs))
def robust_z(vals):
    v = np.array(vals, float); med = np.median(v); mad = np.median(np.abs(v - med)) * 1.4826 or 1e-9
    return (v - med) / mad
by = collections.defaultdict(list)
for i, r in enumerate(recs): by[r['ch']].append(i)
Z = {k: np.zeros(len(recs)) for k in ('w', 'top', 'bot', 'shape', 'adv')}
for ch, idx in by.items():
    for k in ('w', 'top', 'bot'): Z[k][idx] = robust_z([recs[i][k] for i in idx])
    P = np.stack([recs[i]['patch'] for i in idx]); tmpl = np.median(P, 0)
    Z['shape'][idx] = robust_z(np.abs(P - tmpl).mean((1, 2)))
pairs = collections.defaultdict(list)
for i, r in enumerate(recs):
    if r['adv'] is not None: pairs[r['ch']].append(i)
for ch, idx in pairs.items():
    Z['adv'][idx] = robust_z([recs[i]['adv'] for i in idx])
uns = np.array([7 <= r['seg'] <= 15 for r in recs]); has_adv = np.array([r['adv'] is not None for r in recs])
print('\noutlier rate (|robust z| > 5), unsolved vs solved pages:')
for k in ('adv', 'w', 'top', 'bot', 'shape'):
    mask = has_adv if k == 'adv' else np.ones(len(recs), bool)
    out = np.abs(Z[k]) > 5
    a = out[mask & uns].mean(); b = out[mask & ~uns].mean()
    print(f'   {k:6s} unsolved {100*a:5.2f}% (n={int((mask&uns).sum())})   solved {100*b:5.2f}% (n={int((mask&~uns).sum())})   difference {100*(a-b):+.2f} pts')
anyout = np.zeros(len(recs), bool)
for k in Z: anyout |= np.abs(Z[k]) > 5
print('   any    unsolved %.2f%%   solved %.2f%%   (edits removing ~361 doublets would add ~2.8 pts)' % (100 * anyout[uns].mean(), 100 * anyout[~uns].mean()))
pc = collections.Counter(r['page'] for r, o in zip(recs, anyout) if o and 7 <= r['seg'] <= 15)
tot = collections.Counter(r['page'] for r in recs if 7 <= r['seg'] <= 15)
print('unsolved pages with the most outliers (rate):', sorted(((round(pc[p] / tot[p], 3), p, pc[p]) for p in tot), reverse=True)[:6])
