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


def ring(rows):
    top = rows[0]
    if len(rows) == 1:
        return top, [], [], []
    mid = rows[1:-1]
    right = [r[-1] for r in mid]
    bottom = rows[-1][::-1]
    left = [r[0] for r in mid][::-1]
    return top, right, bottom, left


def latin(glyphs):
    return '-'.join(LATIN.get(g, g) for g in glyphs)


def main():
    out = []
    for n, rows in enumerate(read_pages()):
        top, right, bottom, left = ring(rows)
        perim = top + right + bottom + left
        runes_only = all(g in LATIN for g in perim)
        out.append({
            'page': n,
            'image': image_for(n),
            'lines': len(rows),
            'top': ''.join(top) if runes_only else top,
            'right': ''.join(right) if runes_only else right,
            'bottom': ''.join(bottom) if runes_only else bottom,
            'left': ''.join(left) if runes_only else left,
            'circumference': ''.join(perim) if runes_only else perim,
            'length': len(perim),
            'latin': latin(perim),
            'gematria_sum': sum(PRIME.get(g, 0) for g in perim),
            'contains_non_runes': not runes_only,
            # raw columns (every line, top -> bottom) for recombining differently
            'first_column': [r[0] for r in rows],
            'last_column': [r[-1] for r in rows],
        })

    with open(os.path.join(HERE, 'circumference.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    with open(os.path.join(HERE, 'circumference.txt'), 'w', encoding='utf-8') as f:
        f.write('Liber Primus page circumferences, clockwise from top-left: '
                'top | right | bottom | left\n')
        f.write('page  image   lines  len  circumference\n')
        for p in out:
            parts = [p['top'], p['right'], p['bottom'], p['left']]
            if p['contains_non_runes']:
                parts = [' '.join(x) for x in parts]
            f.write('%-5d %-7s %-6d %-4d %s\n' % (
                p['page'], p['image'], p['lines'], p['length'], ' | '.join(parts)))
    print('wrote %d pages' % len(out))


if __name__ == '__main__':
    main()
