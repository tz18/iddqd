# Liber Primus Workbench

An interactive viewer for working on the Liber Primus by hand: every rune page
scan with the transcription laid over it, word by word or rune by rune.

## Run it

`index.html` loads `data/lp.json` with `fetch`, so serve the repository rather
than opening the file directly:

```sh
python3 -m http.server 8000
# then open http://localhost:8000/liber-primus__explorer/
```

Page images are read from `img/` if present, otherwise from
`../liber-primus__images--full/`.

## What it does

- **Overlays:** image only, runes, Latin transliteration, Gematria Primus value or
  sum, deciphered plaintext, plaintext GP. Choose whole words or single runes.
  The Cover slider sets how much the labels hide the scan.
- **Sums:** clause sums (bracket under each clause, total at its end), line sums
  in the margin, page totals, prime-sum words, runes left unencrypted. Sums can be
  taken from the ciphertext or the plaintext.
- **Draw line:** drag through words to build an ordered selection. You get its
  cipher and plaintext sums, factors, primality, mod 29 and rune count, and Copy
  puts it on the clipboard as a table. In Select mode, click a word to select it
  and shift-click to add more.
- **Circumference:** outlines and numbers each page's outer ring of runes,
  clockwise from top-left, with drop caps filling the left edge. Same rules as
  `../liber-primus__circumference`.
- **Cipher bench:** plaintext is computed live in the browser for each segment
  (the `$` sections). The settings are invert (atbash), shift, key stream (key
  word or numbers, primes, totient of primes, Fibonacci), add or subtract,
  stream offset, where the key restarts (segment, page, paragraph, clause, line
  or word), and positions to leave unencrypted. You can also write your own
  function `(c, j, ctx) => index`. Solved segments start with their published
  keys. "Apply to all unsolved" copies the current settings to every unsolved
  segment.
- **Find:** search the whole book for words with a given sum, or a given rune or
  Latin spelling, in ciphertext or plaintext.

Keyboard: ← → change page, + − 0 zoom, Esc clears the selection. Ctrl/⌘ + wheel
zooms. `#page-12` in the URL opens page 12.

## Data pipeline

1. `segment.py` finds each glyph of the master transcription in the page scans
   and writes `data/layout.json`. It needs Pillow, numpy and scipy. Steps:
   - find ink components;
   - remove frames and drop caps (from `../liber-primus__circumference/drop_caps.json`);
   - group the components into rows;
   - align the rows to transcription lines;
   - assign the boxes in each line, using per-rune widths learned from the lines
     that matched exactly.

   About 86% of lines match glyph-for-glyph. The rest are fitted and may be off
   by a rune in places.
2. `build_data.py` writes `data/lp.json`: the pages, the line items with their
   boxes, and the default cipher for each segment.

### Default ciphers and unencrypted F positions

| Segment | Section | Cipher |
|---|---|---|
| 0 | A Warning | atbash |
| 1 | Welcome | Vigenère `DIVINITY`, unencrypted at 48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514 |
| 2 | Some Wisdom | plain |
| 3 | A Koan | atbash + 3 |
| 4 | The Loss of Divinity | plain |
| 5 | A Koan (the Circumference) | Vigenère `FIRFUMFERENFE`, unencrypted at 49, 58 |
| 6 | An Instruction | plain |
| 7–15 | unsolved | plain |
| 16 | An End | totient of primes, unencrypted at 56 |
| 17 | Parable | plain |

Positions count runes within the segment. The unencrypted positions are where a
ciphertext ᚠ is a plaintext F left as-is ("clear text F is not encrypted"). They
were found by trying both readings at every ᚠ and keeping the one that produces
dictionary words. The resulting plaintext matches the published translations.

The rune font is BabelStone Runic Beorhtnoth (SIL Open Font License), from
`../ttf`.
