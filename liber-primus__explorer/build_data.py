#!/usr/bin/env python3
"""Turn data/layout.json (from segment.py) into data/lp.json for the explorer.

lp.json:
  segments: [{name, solved, cipher}]   default cipher per $-segment (known solutions)
  pages:    [{page, img, w, h, lines: [{s, p, c, t}]}]
     s/p/c = segment / paragraph / chapter index
     t     = items; glyphs are [kind, text, x0, y0, x1, y1] (image pixels),
             separators are [kind, text]
     kind  : r rune, n number, h hex char, - word separator, . clause separator

Cipher positions count runes within the segment (numbers and hex excluded).
The F-skip positions were found by decrypting with each key and keeping, at
every ciphertext F, whichever choice yields dictionary words (checked against
the published translations).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

SEGMENTS = [
    ('A Warning', True, {'type': 'atbash', 'shift': 0}),
    ('Welcome', True, {'type': 'vigenere', 'key': [23, 10, 1, 10, 9, 10, 16, 26],
                       'keyText': 'DIVINITY',
                       'skips': [48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514]}),
    ('Some Wisdom', True, {'type': 'plain'}),
    ('A Koan', True, {'type': 'atbash', 'shift': 3}),
    ('The Loss of Divinity', True, {'type': 'plain'}),
    ('A Koan (the Circumference)', True, {'type': 'vigenere',
                                          'key': [0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18],
                                          'keyText': 'FIRFUMFERENFE', 'skips': [49, 58]}),
    ('An Instruction', True, {'type': 'plain'}),
] + [('Unsolved %d' % i, False, {'type': 'plain'}) for i in range(1, 10)] + [
    ('An End', True, {'type': 'totient', 'skips': [56]}),
    ('Parable', True, {'type': 'plain'}),
]

KIND = {'rune': 'r', 'num': 'n', 'hex': 'h'}


def main():
    with open(os.path.join(HERE, 'data', 'layout.json'), encoding='utf-8') as f:
        layout = json.load(f)
    pages = []
    for pg in layout:
        lines = []
        for l in pg['lines']:
            boxes = iter(l['boxes'])
            t = []
            for kind, text in l['items']:
                if kind == 'sep':
                    t.append([text, text])
                else:
                    b = next(boxes)
                    t.append([KIND[kind], text] + ([int(v) for v in b] if b else []))
            lines.append({'s': l['seg'], 'p': l['para'], 'c': l['chap'], 't': t})
        pages.append({'page': pg['page'], 'img': pg['image'], 'w': pg['w'], 'h': pg['h'],
                      'lines': lines})
    nseg = max(l['s'] for p in pages for l in p['lines']) + 1
    assert nseg == len(SEGMENTS), (nseg, len(SEGMENTS))
    out = {
        'segments': [{'name': n, 'solved': s, 'cipher': c} for n, s, c in SEGMENTS],
        'pages': pages,
    }
    with open(os.path.join(HERE, 'data', 'lp.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print('pages', len(pages), 'segments', nseg,
          'bytes', os.path.getsize(os.path.join(HERE, 'data', 'lp.json')))


if __name__ == '__main__':
    main()
