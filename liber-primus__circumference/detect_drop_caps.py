#!/usr/bin/env python3
"""Find the large red drop-cap runes in the page images and record which
transcription lines each one spans. Writes drop_caps.json, which
extract_circumference.py uses for its "visual" circumference.

Needs Pillow, numpy and scipy (pip install pillow numpy scipy).

Method:
  * a drop cap is a connected red region taller than 300px (normal text and red
    title lines are ~115px tall);
  * text lines are horizontal bands of ink (red or black) outside the cap;
  * the cap's own line is matched to a transcription line that starts a page or
    follows a paragraph/segment/chapter marker, choosing the one closest to the
    number of text bands above the cap;
  * the cap spans its own line plus the following text lines that start above
    the first ink found directly below the cap (i.e. lines indented past it),
    limited to the lines left on the page.
Results were checked by eye against crops of every cap; OVERRIDES holds the
cases the heuristic gets wrong.
"""
import json
import os
import re

import numpy as np
from PIL import Image
from scipy import ndimage

import extract_circumference as ec

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(HERE, '..', 'liber-primus__images--full')
TEXT_X = (560, 1840)  # horizontal band holding the text column

# (page, line) -> span, checked by eye
OVERRIDES = {
    (7, 6): 3,  # third line is a lone rune too small to register as a text band
}


def section_starts():
    """For each page, transcription line indices that start a page/section."""
    with open(ec.SRC, encoding='utf-8') as f:
        lines = f.read().split('\n')
    start = next(i for i, l in enumerate(lines) if re.search('[%s]' % ec.RUNES, l))
    pages, cur, idx, mark = [], [], 0, True
    for l in lines[start:]:
        l = l.strip()
        if '%' in l:
            if idx:
                pages.append(cur)
            cur, idx, mark = [], 0, True
        elif l in ec.MARKERS:
            mark = True
        elif l and ec.tokenize(l):
            if mark:
                cur.append(idx)
            idx += 1
            mark = False
    if idx:
        pages.append(cur)
    return pages


def bands(mask):
    on = mask[:, TEXT_X[0]:TEXT_X[1]].sum(1) > 40
    out, y = [], 0
    while y < len(on):
        if on[y]:
            s = y
            while y < len(on) and on[y]:
                y += 1
            if y - s > 40:
                out.append((s, y))
        y += 1
    return out


def detect(image):
    a = np.asarray(Image.open(os.path.join(IMAGES, image)).convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 130) & (g < 90) & (b < 90)
    ink = (a.sum(-1) < 300) | red
    lab, _ = ndimage.label(ndimage.binary_closing(red, iterations=3))
    caps = [s for s in ndimage.find_objects(lab) if s[0].stop - s[0].start > 300]
    m = ink.copy()
    for s in caps:
        m[s[0].start:s[0].stop, s[1].start:s[1].stop + 20] = False
    return caps, bands(m), m


def main():
    starts = section_starts()
    n_lines = [len(p) for p in ec.read_pages()]
    out = []
    for n in range(len(starts)):
        image = ec.image_for(n)
        caps, runs, m = detect(image)
        used = set()
        for s in sorted(caps, key=lambda s: s[0].start):
            y0, y1 = s[0].start, s[0].stop
            x0, x1 = s[1].start, s[1].stop
            # text bands above the cap (ignore tall picture/decoration bands)
            above = sum(1 for a, b in runs if b <= y0 + 10 and b - a <= 150)
            cand = [c for c in starts[n] if c not in used]
            line = min(cand, key=lambda c: abs(c - above))
            used.add(line)
            # first row below the cap with ink in the cap's own columns
            col = m[y1:, x0:x1].sum(1) > 5
            stop = y1 + int(np.argmax(col)) if col.any() else m.shape[0]
            beside = sum(1 for a, b in runs if y0 + 100 <= a and b <= stop + 20)
            span = min(1 + beside, n_lines[n] - line)
            span = OVERRIDES.get((n, line), span)
            out.append({'page': n, 'image': image, 'line': line,
                        'span': span, 'y': [int(y0), int(y1)]})
            print('page %-3d %s line %-2d span %d' % (n, image, line, span))
    with open(os.path.join(HERE, 'drop_caps.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
