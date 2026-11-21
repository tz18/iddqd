#!/usr/bin/env python3
"""Locate every glyph of the master transcription in the page images.

Writes data/pages.json for the explorer. Needs Pillow, numpy and scipy.

Steps per page:
  1. ink = dark or red pixels; large red drop caps are cut out and handled separately;
  2. connected components of glyph size are kept (decorations are too big or too small);
  3. components are grouped into rows by vertical position;
  4. rows are aligned to transcription lines by dynamic programming on glyph counts
     (rows that match nothing - picture fragments, frames - are skipped);
  5. within a row, components overlapping horizontally are merged, separator dots are
     dropped, and the remaining boxes are assigned in order to the line's glyphs
     (merging/splitting at the most likely places when the counts disagree).
Lines that cannot be matched fall back to evenly spaced boxes and are flagged.
"""
import json
import os
import re
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'liber-primus__circumference'))
import extract_circumference as ec  # noqa: E402

IMAGES = os.path.join(ROOT, 'liber-primus__images--full')
RUNES = ec.RUNES


def parse():
    """Transcription -> pages of lines; each line is a list of items
    (kind, text) with kind in rune/num/hex/word/clause, plus structural ids."""
    with open(ec.SRC, encoding='utf-8') as f:
        raw = f.read().split('\n')
    start = next(i for i, l in enumerate(raw) if re.search('[%s]' % RUNES, l))
    pages, lines = [], []
    seg = para = chap = 0
    for l in raw[start:]:
        l = l.strip()
        if not l:
            continue
        if '%' in l:
            if lines:
                pages.append(lines)
            lines = []
            continue
        if l == '$':
            seg += 1
            para += 1
            continue
        if l == '&':
            para += 1
            continue
        if l == '§':
            chap += 1
            continue
        items = []
        hexline = not re.search('[%s]' % RUNES, l) and '-' not in l
        for m in re.finditer('[%s]|[0-9A-Za-z]+|[-.]' % RUNES, l.rstrip('/')):
            t = m.group(0)
            if t in RUNES:
                items.append(['rune', t])
            elif t == '-':
                items.append(['sep', '-'])
            elif t == '.':
                items.append(['sep', '.'])
            elif hexline:
                items += [['hex', c] for c in t]
            else:
                items.append(['num', t])
        lines.append({'items': items, 'seg': seg, 'para': para, 'chap': chap,
                      'text': l})
    if lines:
        pages.append(lines)
    return pages


def glyph_count(line):
    """Expected number of ink components (digits/letters count individually)."""
    n = 0
    for k, t in line['items']:
        if k in ('rune', 'hex'):
            n += 1
        elif k == 'num':
            n += len(t)
    return n


def load(image):
    a = np.asarray(Image.open(os.path.join(IMAGES, image)).convert('RGB')).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 130) & (g < 90) & (b < 90)
    ink = (a.sum(-1) < 330) | red
    # remove long straight strokes (page frames); rune strokes are < ~130px
    vert = ndimage.binary_opening(ink, structure=np.ones((200, 1)))
    horiz = ndimage.binary_opening(ink, structure=np.ones((1, 300)))
    frame = ndimage.binary_dilation(vert | horiz, iterations=2) & ~red
    return ink & ~frame, red


def components(ink, red):
    lab, n = ndimage.label(ndimage.binary_closing(red, iterations=3))
    caps = []
    for i, s in enumerate(ndimage.find_objects(lab)):
        if s[0].stop - s[0].start > 300:
            caps.append((s[1].start, s[0].start, s[1].stop, s[0].stop))
            ink = ink.copy()
            ink[s[0].start:s[0].stop, s[1].start:s[1].stop] = False
    lab, n = ndimage.label(ink, structure=np.ones((3, 3)))
    boxes = []
    for s in ndimage.find_objects(lab):
        y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
        h, w = y1 - y0, x1 - x0
        if h < 8 or w < 3 or h > 200 or w > 260:
            continue
        boxes.append([x0, y0, x1, y1])
    return boxes, caps


def rows_of(boxes):
    """Group boxes into text rows by vertical centre (fixed tolerance, no chaining)."""
    tall = sorted([b for b in boxes if b[3] - b[1] >= 35], key=lambda b: (b[1] + b[3]) / 2)
    rows = []
    for b in tall:
        cy = (b[1] + b[3]) / 2
        h = b[3] - b[1]
        best = None
        for r in rows:
            if abs(cy - r['cy']) < 0.35 * max(r['h'], h) and abs(h - r['h']) < 0.6 * r['h']:
                best = r
                break
        if best is None:
            rows.append({'cy': cy, 'h': h, 'boxes': [b]})
        else:
            best['boxes'].append(b)
            hs = sorted(x[3] - x[1] for x in best['boxes'])
            best['h'] = hs[len(hs) // 2]
            cys = sorted((x[1] + x[3]) / 2 for x in best['boxes'])
            best['cy'] = cys[len(cys) // 2]
    for r in rows:
        r['y0'] = min(x[1] for x in r['boxes'])
        r['y1'] = max(x[3] for x in r['boxes'])
    rows.sort(key=lambda r: r['cy'])
    return rows


def merge_overlapping(boxes, slack=2):
    out = []
    for b in sorted(boxes):
        if out and b[0] < out[-1][2] - slack:
            o = out[-1]
            out[-1] = [min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3])]
        else:
            out.append(list(b))
    return out


def clean_row(boxes, max_gap=130):
    """Drop decoration: keep glyph-height boxes in the biggest horizontal cluster."""
    hs = sorted(b[3] - b[1] for b in boxes)
    med = hs[len(hs) // 2]
    keep = [b for b in boxes if 0.5 * med <= b[3] - b[1] <= 1.25 * med]
    main = [b for b in merge_overlapping(keep) if b[3] - b[1] <= 1.3 * med]
    if not main:
        return []
    clusters, cur = [], [main[0]]
    for b in main[1:]:
        if b[0] - cur[-1][2] > max_gap:
            clusters.append(cur)
            cur = [b]
        else:
            cur.append(b)
    clusters.append(cur)
    return max(clusters, key=len)


def fit(boxes, n):
    """Force len(boxes) == n by merging closest neighbours / splitting widest."""
    boxes = [list(b) for b in boxes]
    while len(boxes) > n and len(boxes) > 1:
        gaps = [boxes[i + 1][0] - boxes[i][2] for i in range(len(boxes) - 1)]
        i = int(np.argmin(gaps))
        a, b = boxes[i], boxes[i + 1]
        boxes[i:i + 2] = [[min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]]
    while len(boxes) < n and boxes:
        i = int(np.argmax([b[2] - b[0] for b in boxes]))
        b = boxes[i]
        m = (b[0] + b[2]) // 2
        boxes[i:i + 1] = [[b[0], b[1], m, b[3]], [m, b[1], b[2], b[3]]]
    return boxes


WIDTHS = {}  # glyph char -> median width / row height (learned on exact lines)
GAP = 0.18


def glyph_chars(items):
    out = []
    for k, t in items:
        if k == 'num':
            out += list(t)
        elif k != 'sep':
            out.append(t)
    return out


def assign(comps, chars, h):
    """DP alignment of components to expected glyph chars using the width model.
    Returns one box (or None) per char."""
    m, n = len(comps), len(chars)
    if n == 0:
        return []
    if not comps:
        return [None] * n
    ew = [WIDTHS.get(c, 0.4) * h for c in chars]
    INF = float('inf')
    cost = [[INF] * (n + 1) for _ in range(m + 1)]
    back = {}
    cost[0][0] = 0.0

    def relax(i, j, ni, nj, c, how):
        if c < cost[ni][nj]:
            cost[ni][nj] = c
            back[(ni, nj)] = (i, j, how)

    for i in range(m + 1):
        for j in range(n + 1):
            c = cost[i][j]
            if c == INF:
                continue
            if i < m:
                relax(i, j, i + 1, j, c + 1.2, ('skip',))
            if j < n:
                relax(i, j, i, j + 1, c + 1.5, ('miss',))
            for k in (1, 2, 3, 4):  # one component covers k glyphs
                if i < m and j + k <= n:
                    w = comps[i][2] - comps[i][0]
                    exp = sum(ew[j:j + k]) + (k - 1) * GAP * h
                    relax(i, j, i + 1, j + k, c + abs(w - exp) / h * 2 + (k - 1) * 0.15, ('cover', k))
            for k in (2, 3):  # k components make one glyph
                if i + k <= m and j < n:
                    w = comps[i + k - 1][2] - comps[i][0]
                    relax(i, j, i + k, j + 1, c + abs(w - ew[j]) / h * 2 + 0.3 * (k - 1), ('join', k))
    out = [None] * n
    i, j = m, n
    while (i, j) in back:
        pi, pj, how = back[(i, j)]
        if how[0] == 'cover':
            b = comps[pi]
            k = how[1]
            tot = sum(ew[pj:pj + k]) or 1
            x = b[0]
            span = b[2] - b[0]
            for t in range(k):
                w = span * ew[pj + t] / tot
                out[pj + t] = [int(x), b[1], int(x + w), b[3]]
                x += w
        elif how[0] == 'join':
            bs = comps[pi:i]
            out[pj] = [min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs)]
        i, j = pi, pj
    # interpolate misses between neighbours
    for t in range(n):
        if out[t] is None:
            prev = next((out[u] for u in range(t - 1, -1, -1) if out[u]), None)
            nxt = next((out[u] for u in range(t + 1, n) if out[u]), None)
            w = ew[t]
            if prev:
                x0 = prev[2] + GAP * h * 0.5
                out[t] = [int(x0), prev[1], int(x0 + w), prev[3]]
            elif nxt:
                x1 = nxt[0] - GAP * h * 0.5
                out[t] = [int(x1 - w), nxt[1], int(x1), nxt[3]]
    return out


def align(rows, lines):
    """DP: assign each transcription line to a distinct row, in order."""
    R, L = len(rows), len(lines)
    INF = 10 ** 9
    hs = sorted(r['h'] for r in rows if r['n'] >= 8) or [114]
    hmed = hs[len(hs) // 2]
    cost = [[INF] * (L + 1) for _ in range(R + 1)]
    back = {}
    cost[0][0] = 0
    for i in range(R + 1):
        for j in range(L + 1):
            c = cost[i][j]
            if c >= INF:
                continue
            if i < R:  # skip row
                pen = 2 + len(rows[i]['boxes']) * 0.2
                if c + pen < cost[i + 1][j]:
                    cost[i + 1][j] = c + pen
                    back[(i + 1, j)] = (i, j, False)
            if i < R and j < L:
                exp = glyph_count(lines[j])
                got = rows[i]['n']
                pen = abs(exp - got) / max(exp, 1) * 10
                if any(k == 'rune' for k, _ in lines[j]['items']):
                    pen += abs(rows[i]['h'] / hmed - 1) * 8
                if c + pen < cost[i + 1][j + 1]:
                    cost[i + 1][j + 1] = c + pen
                    back[(i + 1, j + 1)] = (i, j, True)
    # best end state uses all lines
    i = min(range(R + 1), key=lambda i: cost[i][L])
    j = L
    match = {}
    while (i, j) in back:
        pi, pj, m = back[(i, j)]
        if m:
            match[pj] = pi
        i, j = pi, pj
    return match


_CACHE = {}


def page_layout(n, lines, image, caps_info, learn=None):
    if image not in _CACHE:
        ink, red = load(image)
        boxes, caps = components(ink, red)
        rows = rows_of(boxes)
        for r in rows:
            r['main'] = clean_row(r['boxes'])
            r['n'] = len(r['main'])
        # text column: from well-populated rows; then drop anything outside it
        full = [r for r in rows if r['n'] >= 8]
        if full:
            lefts = sorted(r['main'][0][0] for r in full)
            rights = sorted(r['main'][-1][2] for r in full)
            colL = lefts[len(lefts) // 5] - 60
            if caps:  # lines beside a drop cap are indented; the column starts at the cap
                colL = min(colL, min(c[0] for c in caps) - 20)
            colR = rights[len(rights) * 4 // 5] + 60
            for r in rows:
                inside = [b for b in r['boxes'] if b[0] >= colL and b[2] <= colR]
                r['main'] = clean_row(inside) if inside else []
                r['n'] = len(r['main'])
            rows = [r for r in rows if r['n']]
        _CACHE[image] = (ink.shape, caps, rows)
    (H, W), caps, rows = _CACHE[image]
    cap_lines = {c['line']: c for c in caps_info}
    caps = sorted(caps, key=lambda c: c[1])
    # a cap line's own row lacks its first rune (the cap): count it in
    match = align(rows, [dict(l, items=l['items'][1:] if i in cap_lines and l['items'] and l['items'][0][0] == 'rune' else l['items']) for i, l in enumerate(lines)])
    out_lines = []
    exact = 0
    for j, line in enumerate(lines):
        glyph_items = [k for k in line['items'] if k[0] != 'sep']
        boxes_out = []
        flag = 'ok'
        cap_box = None
        if j in cap_lines and caps:
            ci = [c for c in caps_info if c['line'] == j][0]
            cand = [c for c in caps if abs(c[1] - ci['y'][0]) < 20]
            if cand:
                cap_box = list(cand[0])
        if j in match:
            r = rows[match[j]]
            main = r['main']
            if cap_box:
                main = [b for b in main if b[0] > cap_box[2] - 5]
            chars = glyph_chars(glyph_items)
            if cap_box:
                chars = chars[1:]
            need = len(chars)
            if len(main) == need:
                exact += 1
                gb = [list(b) for b in main]
                if learn is not None:
                    h = np.median([b[3] - b[1] for b in main])
                    for c, b in zip(chars, main):
                        learn.setdefault(c, []).append((b[2] - b[0]) / h)
            else:
                flag = 'fitted'
                h = np.median([b[3] - b[1] for b in main]) if main else 114
                gb = assign(main, chars, h)
            if cap_box:
                gb = [cap_box] + gb
            per_item = [len(t) if k == 'num' else 1 for k, t in glyph_items]
            k = 0
            for c in per_item:
                bs = [b for b in gb[k:k + c] if b]
                k += c
                if bs:
                    boxes_out.append([min(b[0] for b in bs), min(b[1] for b in bs),
                                      max(b[2] for b in bs), max(b[3] for b in bs)])
                else:
                    boxes_out.append(None)
            y0, y1 = r['y0'], r['y1']
        else:
            flag = 'guessed'
            boxes_out = [None] * len(glyph_items)
        out_lines.append({'flag': flag, 'boxes': boxes_out})
    # fill guessed lines: interpolate y between neighbours, spread x evenly
    ys = [(j, [b for b in l['boxes'] if b]) for j, l in enumerate(out_lines)]
    known = [(j, np.median([b[1] for b in bs]), np.median([b[3] for b in bs])) for j, bs in ys if bs]
    for j, l in enumerate(out_lines):
        if l['flag'] != 'guessed' or not known:
            continue
        before = [k for k in known if k[0] < j]
        after = [k for k in known if k[0] > j]
        if before and after:
            a, b = before[-1], after[0]
            t = (j - a[0]) / (b[0] - a[0])
            y0 = a[1] + t * (b[1] - a[1]); y1 = a[2] + t * (b[2] - a[2])
        elif before:
            a = before[-1]; pitch = 188
            y0 = a[1] + pitch * (j - a[0]); y1 = a[2] + pitch * (j - a[0])
        else:
            b = after[0]; pitch = 188
            y0 = b[1] - pitch * (b[0] - j); y1 = b[2] - pitch * (b[0] - j)
        m = len(l['boxes'])
        x0, x1 = 600, 1800
        l['boxes'] = [[int(x0 + (x1 - x0) * i / m), int(y0), int(x0 + (x1 - x0) * (i + 1) / m) - 8, int(y1)] for i in range(m)]
    return out_lines, W, H, exact


def main():
    pages = parse()
    with open(os.path.join(ROOT, 'liber-primus__circumference', 'drop_caps.json')) as f:
        caps = json.load(f)
    only = [int(a) for a in sys.argv[1:]]
    cache = {}
    learn = {}
    for n, lines in enumerate(pages):
        if only and n not in only:
            continue
        page_layout(n, lines, ec.image_for(n), [c for c in caps if c['page'] == n], learn)
    for c, v in learn.items():
        WIDTHS[c] = float(np.median(v))
    print('learned widths for %d glyphs' % len(WIDTHS))
    json.dump(WIDTHS, open(os.environ.get('WIDTHS_OUT', os.devnull), 'w'))
    stats = []
    result = []
    for n, lines in enumerate(pages):
        if only and n not in only:
            continue
        image = ec.image_for(n)
        ci = [c for c in caps if c['page'] == n]
        out, W, H, exact = page_layout(n, lines, image, ci)
        flags = [l['flag'] for l in out]
        stats.append((n, image, len(lines), exact, flags.count('fitted'), flags.count('guessed')))
        print('page %2d %s lines %2d exact %2d fitted %2d guessed %2d' % stats[-1], flush=True)
        result.append({'page': n, 'image': image, 'w': W, 'h': H, 'lines': [
            dict(l, flag=o['flag'], boxes=o['boxes'], items=l['items']) for l, o in zip(lines, out)]})
    if not only:
        os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)
        with open(os.path.join(HERE, 'data', 'layout.json'), 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, separators=(',', ':'))
    tot = [sum(s[i] for s in stats) for i in (2, 3, 4, 5)]
    print('TOTAL lines %d exact %d fitted %d guessed %d' % tuple(tot))


if __name__ == '__main__':
    main()
