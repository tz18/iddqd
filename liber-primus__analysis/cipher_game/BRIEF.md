# The cipher game

A rehearsal for the unsolved Liber Primus pages. A "Cicada" encrypts a known English plaintext (about 600 words,
written in the voice of the solved LP pages) with a cipher designed to reproduce the statistical findings of the
unsolved pages. A "Solver" studies the ciphertext blind and compares it with the unsolved pages. "Mr Annoying"
judges whether the cipher is something Cicada 3301 could plausibly have used and hinted at.

All paths below are relative to `/home/user/iddqd/liber-primus__analysis/`.

## Roles and rules

| Role | May read | Must not read | Writes |
|---|---|---|---|
| Cicada | everything | (nothing off-limits) | `cipher_game/secret/*`, `cipher_game/roundN/ciphertext.json`, `cipher_game/roundN/ciphertext.txt` |
| Solver | this brief, `cipher_game/roundN/ciphertext.*`, the unsolved-page data and analysis scripts, earlier `cipher_game/round*/solver_methods.md` | `cipher_game/secret/`, `cipher_game/round*/cicada_*`, `cipher_game/round*/annoying_*`, git history or `git` commands of any kind | `cipher_game/roundN/solver_report.md`, `cipher_game/roundN/solver_methods.md` (methods only, never plaintext), and if it decrypts anything `cipher_game/roundN/solver_decryption.txt` |
| Mr Annoying | everything, including `cipher_game/secret/` | (nothing off-limits) | `cipher_game/roundN/annoying_report.md` |

Nobody commits or pushes. Nobody installs packages.

## Runes

Gematria Primus order, index 0-28 (Latin, GP value):
F 2, U 3, TH 5, O 7, R 11, C/K 13, G 17, W 19, H 23, N 29, I 31, J 37, EO 41, P 43, X 47, S/Z 53, T 59, B 61, E 67,
M 71, L 73, NG/ING 79, OE 83, D 89, A 97, AE 101, Y 103, IA/IO 107, EA 109.
Runes as characters: `ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ` (same order). V is written U, Q as CW.

## Ciphertext format (Cicada writes, Solver reads)

- `ciphertext.json`: `{"clauses": [ [ [r, r, ...], [r, ...] ], ... ]}` - a list of clauses, each a list of words, each a
  list of rune indices 0-28.
- `ciphertext.txt`: the same in runes, words separated by `-`, one clause per line ending with `.`.

The plaintext's clauses are its lines (headings included). Word breaks in the ciphertext are the cipher's business:
keeping, moving or removing them are all allowed, but whatever is shown is what the Solver gets.

## The unsolved pages: data and targets

Data: `lp_common.py` gives `UNS`, a list of dicts for every unsolved rune with keys `c` (rune index), `word`,
`clause`, `seg`, `page`, `line`. Earlier analysis scripts and their results are described in `README.md` and
`results/`; `findings.html` is the summary page.

Targets measured on the unsolved pages (12,956 runes, 2,896 words, 168 clauses). The generated plaintext is only
~600 words, so compare rates with their uncertainty, not exact values.

| # | Property | Unsolved value | For comparison |
|---|---|---|---|
| 1 | Doublets (rune equal to its neighbour) | 0.66% overall; 0.63% inside words, 0.81% across word gaps | 3.45% for flat random runes |
| 2 | Doublets' place inside words | same as random positions (27% first rune, 51% middle, 22% last) | not where any one plaintext letter would sit |
| 3 | Rune frequencies | flat: chi2 26 on 28 df; mean GP value per rune 51.6 | English plaintext: mean ~45 |
| 4 | F count | 3.5%, at the flat level | a "plaintext F passes through" rule would give ~5% |
| 5 | Word lengths in runes (share for 1..9, 10+) | .029 .155 .249 .177 .109 .088 .075 .054 .027 .038, mean 4.47 | English in LP spelling: 2-rune share ~.24; spelled letter by letter: ~.16 |
| 6 | Word-length order | lag-1 correlation -0.015 (none); clause-final words 4.2 runes, not long | English: lag-1 -0.13, clause-final words ~5.5 |
| 7 | Same rune 5 apart inside a word | 4.9% (z +3.7); across word gaps 3.46% (baseline); other lags baseline | English's own within-word distance-5 rate is ~5% |
| 8 | Short clauses (<= 31 runes) with prime GP sum | 18 of 54 (33%) | ~15% by chance |
| 9 | Clause lengths | English-sentence-like; only 2 one-word clauses | |
| 10 | Periodic key | none for periods 1-100, raw or after autokey removal (d[i] = c[i] - c[i-1] mod 29) | |
| 11 | Pass-through rune | none detectable | |
| 12 | Exact repeats | one 6-rune, two-word repeat (DJU BEI) in 12,956 runes | optional |

## What Mr Annoying checks

A cipher counts only if an intended solver could decrypt it with information Cicada could plausibly hint at:
- the key is short, or derived from something public (LP text, primes, totient, a keyword, a book);
- every choice the encryptor made can be recovered by the decryptor from ciphertext plus key - no free per-word or
  per-clause choices unless a stated rule fixes them;
- complexity in proportion to the solved LP ciphers (atbash; Vigenere with the key DIVINITY and unencrypted F;
  a totient-of-primes stream);
- the number of free parameters and the key size are stated and small.
