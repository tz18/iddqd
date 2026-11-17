#!/usr/bin/env python3
"""Extract the circumference (outer ring of glyphs) of every Liber Primus page.

Source: ../liber-primus__transcription--master/liber-primus__transcription--master.txt

Order is clockwise starting top-left:
  top    : every glyph of the first line, left -> right
  right  : last glyph of each middle line, top -> bottom
  bottom : every glyph of the last line, right -> left
  left   : first glyph of each middle line, bottom -> top
Corners are counted once (they belong to top/bottom).

Glyphs: each rune is one glyph. Word/clause separators (- .) are not glyphs.
Numbers written with separators (e.g. "272-138", base-60 "2M-0w") count as one
glyph per number; separator-less hex lines count one glyph per character.

Drop caps: many sections open with a large red rune spanning several lines
(listed in drop_caps.json, produced by detect_drop_caps.py from the images).
On those lines the cap is the leftmost glyph, so the main output puts the cap
(once) on the left edge in place of those lines' own first runes. The ring
that ignores drop caps is kept under "ignoring_drop_caps".

Page numbering: `page` is the index of the rune page in the transcription;
`image` is the matching file in ../liber-primus__images--full (images 00 and 02
are the Latin title/chapter pages, which contain no runes).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'liber-primus__transcription--master',
                   'liber-primus__transcription--master.txt')

# Gematria Primus: rune -> (latin, prime value)
GP = [
    ('ᚠ', 'F', 2), ('ᚢ', 'U', 3), ('ᚦ', 'TH', 5), ('ᚩ', 'O', 7), ('ᚱ', 'R', 11),
    ('ᚳ', 'C', 13), ('ᚷ', 'G', 17), ('ᚹ', 'W', 19), ('ᚻ', 'H', 23), ('ᚾ', 'N', 29),
    ('ᛁ', 'I', 31), ('ᛄ', 'J', 37), ('ᛇ', 'EO', 41), ('ᛈ', 'P', 43), ('ᛉ', 'X', 47),
    ('ᛋ', 'S', 53), ('ᛏ', 'T', 59), ('ᛒ', 'B', 61), ('ᛖ', 'E', 67), ('ᛗ', 'M', 71),
    ('ᛚ', 'L', 73), ('ᛝ', 'NG', 79), ('ᛟ', 'OE', 83), ('ᛞ', 'D', 89), ('ᚪ', 'A', 97),
    ('ᚫ', 'AE', 101), ('ᚣ', 'Y', 103), ('ᛡ', 'IA', 107), ('ᛠ', 'EA', 109),
]
LATIN = {r: l for r, l, _ in GP}
PRIME = {r: p for r, _, p in GP}
RUNES = ''.join(LATIN)

MARKERS = {'&', '$', '§'}  # paragraph, segment, chapter: not page content


def image_for(page):
    return '%02d.jpg' % (1 if page == 0 else page + 2)


def tokenize(line):
    line = line.rstrip('/')
    if re.search('[%s]' % RUNES, line) or '-' in line:
        return re.findall('[%s]|[0-9A-Za-z]+' % RUNES, line)
    return re.findall('[0-9A-Za-z]', line)  # separator-less hex line


def read_pages():
    with open(SRC, encoding='utf-8') as f:
        lines = f.read().split('\n')
    # skip the delimiter legend at the top of the file
    start = next(i for i, l in enumerate(lines) if re.search('[%s]' % RUNES, l))
    pages, cur = [], []
    for l in lines[start:]:
        l = l.strip()
        if '%' in l:
            if cur:
                pages.append(cur)
            cur = []
        elif l and l not in MARKERS:
            toks = tokenize(l)
            if toks:
                cur.append(toks)
    if cur:
        pages.append(cur)
    return pages


def ring(rows, caps=()):
    """Clockwise ring of (line, index) positions.

    caps: (line, span) drop caps. A drop cap is the first glyph of `line` and
    is the leftmost glyph of every line it spans, so those lines contribute the
    cap (once) to the left edge instead of their own first glyph."""
    last = len(rows) - 1
    cover = {}
    for k, span in caps:
        for i in range(k, min(k + span, len(rows))):
            cover[i] = (k, 0)
    top = [(0, j) for j in range(len(rows[0]))]
    if last == 0:
        return top, [], [], []
    right = [(i, len(rows[i]) - 1) for i in range(1, last)]
    bottom = [(last, j) for j in reversed(range(len(rows[last])))]
    if last in cover and cover[last] != (last, 0):
        bottom.append(cover[last])  # cap reaches the bottom-left corner
    seen = set(top + right + bottom)
    left = []
    for i in range(last - 1, 0, -1):
        pos = cover.get(i, (i, 0))
        if pos not in seen:
            left.append(pos)
            seen.add(pos)
    return top, right, bottom, left


def latin(glyphs):
    return '-'.join(LATIN.get(g, g) for g in glyphs)


def describe(rows, caps):
    sides = [[rows[i][j] for i, j in side] for side in ring(rows, caps)]
    perim = sum(sides, [])
    runes_only = all(g in LATIN for g in perim)
    fmt = (lambda x: ''.join(x)) if runes_only else (lambda x: x)
    d = {k: fmt(v) for k, v in zip(('top', 'right', 'bottom', 'left'), sides)}
    d.update({
        'circumference': fmt(perim),
        'length': len(perim),
        'latin': latin(perim),
        'gematria_sum': sum(PRIME.get(g, 0) for g in perim),
    })
    return d, runes_only


def load_drop_caps():
    path = os.path.join(HERE, 'drop_caps.json')
    caps = {}
    if os.path.exists(path):
        with open(path) as f:
            for c in json.load(f):
                caps.setdefault(c['page'], []).append((c['line'], c['span']))
    return caps


def write_txt(name, header, entries):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8') as f:
        f.write(header + '\n')
        f.write('page  image   lines  len  top | right | bottom | left\n')
        for p, d in entries:
            parts = [d['top'], d['right'], d['bottom'], d['left']]
            if p['contains_non_runes']:
                parts = [' '.join(x) for x in parts]
            f.write('%-5d %-7s %-6d %-4d %s\n' % (
                p['page'], p['image'], p['lines'], d['length'], ' | '.join(parts)))


def main():
    drop_caps = load_drop_caps()
    out = []
    for n, rows in enumerate(read_pages()):
        caps = drop_caps.get(n, [])
        visual, runes_only = describe(rows, caps)
        plain, _ = describe(rows, [])
        p = {'page': n, 'image': image_for(n), 'lines': len(rows),
             'drop_caps': [{'line': k, 'span': s, 'rune': rows[k][0]} for k, s in caps]}
        p.update(visual)
        p['contains_non_runes'] = not runes_only
        p['ignoring_drop_caps'] = plain
        # raw columns (every line, top -> bottom) for recombining differently
        p['first_column'] = [r[0] for r in rows]
        p['last_column'] = [r[-1] for r in rows]
        out.append(p)

    with open(os.path.join(HERE, 'circumference.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    write_txt('circumference.txt',
              'Liber Primus page circumferences as they appear on the page '
              '(drop caps fill the left edge of the lines they span), clockwise '
              'from top-left', [(p, p) for p in out])
    write_txt('circumference_ignoring_drop_caps.txt',
              'Liber Primus page circumferences from the transcription line '
              'starts, ignoring drop caps, clockwise from top-left',
              [(p, p['ignoring_drop_caps']) for p in out])
    print('wrote %d pages (%d with drop caps)' % (len(out), len(drop_caps)))


if __name__ == '__main__':
    main()
