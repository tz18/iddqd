# Round 2 cipher: "the book's prime count multiplies each rune; EA is nothing; the breaks are sorted by the key"

## Method

1. **Spelling: LP digraph spelling**, as on every solved page. TH, NG/ING, EO, OE, AE, IA/IO and EA are single runes;
   K->C, V->U, Q/QU->CW, Z->S; greedy longest match. Each line of `plaintext.txt` is a clause, headings included.
   Result: 40 clauses, 604 words, 2,201 runes (`plaintext_runes.json`; Latin view in `plaintext_runes_latin.txt`).
2. **Numbers.** A rune's number is its Gematria Primus position 1..29 (F=1 ... EA=29), taken mod 29. So EA is 0.
3. **Key: the solved book's running prime sum.** The book B is the solved LP plaintext in page order (A Warning, Welcome,
   Some Wisdom, A Koan, The Loss of Divinity, the Circumference koan, An Instruction, An End, Parable; 2,977 runes,
   as `lp_common.py` decodes them). K_t = (GP(B_0) + ... + GP(B_t)) mod 29, with zero values passed over (0 cannot
   multiply). 2,862 key values, starting at the first rune of the book.
4. **Inner layer: multiply.** y_i = n_i * K_j mod 29. A plaintext EA has n = 0, so y = 0 whatever the key, and the
   key index j does not advance on it (the solved pages' "key waits on the skipped rune" convention).
5. **Outer layer: ciphertext autokey.** c_i = c_{i-1} + y_i mod 29, c_{-1} = 0, one chain through the whole text.
   The ciphertext rune is the one whose number is c (0 -> EA).
6. **Breaks: keyed transposition of the word lengths.** The rune stream stays in plaintext order and clause breaks stay
   where they are. Inside a clause of m words, with a = the key index at the clause's first rune, let
   pi = stable ascending argsort of K_a..K_{a+m-1}. Ciphertext word t gets the length of plaintext word pi(t), and the
   clause's runes are re-cut with those lengths. This is a columnar transposition of the clause's word lengths, with
   the key values as the column order. The breaks the Solver sees are not plaintext word boundaries.

**Decryption** (`decrypt.py`): y = c_i - c_{i-1}. y = 0 gives EA (the key waits). Otherwise n = y * K_j^27 mod 29 and
j += 1. Recording j at each clause start gives pi, and inverting it restores the plaintext word lengths. Nothing is
recovered by guessing: every step is fixed by the ciphertext and the public book. Check (`decrypt_check.txt`): 40
clauses, 604 words, 2,201 runes, 0 rune differences, identical word and clause structure, exact match.

Why each layer is there (one mechanism per target family):
- the ciphertext autokey makes c flat (target 3, 4) whatever the inner layer does;
- multiplication fixes 0, so y = 0 (a doublet) exactly at plaintext EA, and nowhere else (targets 1, 11);
- the running sum makes the multiplier flat and aperiodic. The raw book used as multiplier would not do: the d stream
  would have IoC ~1.06 (chi2 ~170 on 27 df on 2,500 runes, measured), where the unsolved d stream is flat (1.001).
  It is also what defeats the round-1 attack (below);
- the length transposition moves the visible breaks off the plaintext word boundaries. EA's in-word places, English
  word-length order and long clause-final words are then invisible (targets 1-across-gaps, 2, 6).

## Hint text

> THE BOOK YOU HAVE READ IS THE KEY. SUM ITS PRIMES AS YOU READ, AND LET THE SUM, MOD TWENTY NINE, MULTIPLY EACH RUNE;
> WHERE THE SUM IS NOTHING, READ ON. NUMBER THE RUNES FROM ONE: THE LAST IS NOTHING, IT IS NOT ENCRYPTED, AND THE SUM
> WAITS FOR IT. EACH RUNE CARRIES WHAT CAME BEFORE. THE WORDS ARE NOT WHERE THEY SEEM: EACH SENTENCE KEEPS ITS LENGTHS,
> SORTED BY THE SUM.

It fixes the book (the solved pages, in order, from the start), the key transform (running GP sum mod 29, zeros
skipped), the operation (multiply, not add), the zero rune (EA, by numbering from 1), the key-advance rule (the key
waits on EA), the chain (add the previous ciphertext rune), and that the breaks are a key-ordered permutation of each
sentence's word lengths. It leaves open: c_{-1} (0 is the natural try and affects one rune), ascending versus
descending sort and the tie rule (4 combinations, checked by whether the words read). Encrypt and decrypt multiply
by K or by K^-1: the hint says multiply on encryption.

## Results (`selfcheck_output.txt`; uncertainty from 400 clause-aligned unsolved blocks of 604 words, plus exact tests)

| # | Target | Unsolved | Round 2 | Verdict | Mechanism |
|---|---|---|---|---|---|
| 1 | Doublets overall | 0.66% | 1.00% (22/2200); block 0.66 +/- 0.15, z +2.2; Poisson p 0.08 vs 0.66% | **marginal (rate high)** | doublet = plaintext EA, so the rate is f_EA(plaintext): 1.00% for this plaintext; 0.67% for the solved LP plaintext, 0.86-0.88% for Blake |
| 1 | inside / across gaps | 0.63% / 0.79% | 1.06% / 0.83%; Fisher p 0.81 that they differ; share at gaps 23% (unsolved 27%) | **yes** (equal) | the cipher runs continuously over gaps, and the gaps are not plaintext boundaries |
| 2 | Doublet place in word | random | 9/4/4 first/mid/last vs 6.3/6.2/4.6 expected at random places, p 0.37 | **yes** (n = 17, weak test) | breaks re-cut by the key, so EA sits at random places in the visible words |
| 3 | Flat frequencies | chi2 26, mean GP 51.6 | chi2 42.0 (p 0.044); mean GP 49.6 vs flat 51.0 +/- 0.73 (z -2.0); IoC 1.006 | **marginal** | autokey alone makes c flat. With 60 other book offsets the same plaintext gives chi2 27.2 +/- 7.2: offset 0 is a ~2 sd fluctuation, which I did not tune away |
| 4 | F count | 3.5% | 3.45% | **yes** | no pass-through at the ciphertext level |
| 5 | Word lengths (soft) | mean 4.47, 2-rune .155 | mean 3.64, 2-rune .267; chi2 109 on 9 df | **no (soft target; plaintext)** | LP digraph spelling of this plaintext. The cipher keeps each clause's length multiset exactly, so it does not distort lengths |
| 6 | Word-length order | lag-1 -0.015; final 4.2 (mean -0.23) | lag-1 +0.002; final 3.93 = mean +0.28; first = mean -0.09 | **yes** | keyed transposition. The plaintext breaks had lag-1 -0.207, final = mean +1.19, first = mean -0.91 |
| 7 | Lag 5 inside words | 4.9% (z +3.7) | 3.66% (baseline 3.51%) | **no** | no mechanism; I know of no hintable one |
| 8 | Prime short clauses | 33% | 2/19 (11%); p 0.05 vs 33%, 1.00 vs chance | **no** | no mechanism (see below) |
| 9 | Clause lengths | 17.2 words, sd 16.3 | 15.1 words, sd 11.4, 0 one-word clauses; block z about -1 for each | **yes, from the plaintext** | I wrote sentence-length lines this time; the cipher keeps clause breaks. Not a cipher property |
| 10 | Periodic key | none 1-100 | raw best P=47 z +2.1 (p 0.85); d best P=92 z +2.4 (p 0.48); d periods 101-2000: Bonferroni p 1.00 | **yes** | running sum of an English book is aperiodic |
| 11 | Pass-through rune | none | max raw rune z +2.5; max nonzero d z +2.0 | **yes** (soft: +2.5 is a little above the expected max of ~+2) | EA passes only inside the chain, as y = 0 |
| 12 | Exact repeats | one 6-run in 12,956 | longest 4 runes | **yes** (chance) | |
| - | d stream flat apart from 0 | IoC 1.001 | IoC 1.004, chi2 35.0 on 27 df | **yes** | running-sum key is flat; raw book would give IoC ~1.06 |

Summary: clear hits are 1 (equal across gaps), 2, 4, 6, 10, 11, 12 and the flat d stream. 1 (rate) and 3 are marginal
at about 2 sd. 9 matches but comes from the plaintext. 5 is off because of the plaintext and spelling (soft target). The
misses are 7 and 8. Round 1 hit 3, 4, 10, 11, 12 and missed 1, 2 (untestable), 5, 6, 8, 9.

### What this design does not do, and why

- **Doublets are still one plaintext letter (EA).** The brief asked for doublets that are not one plaintext letter. The
  observable signature is gone: the rate is equal inside words and across gaps, and the places are random. But after
  decryption every doublet is an EA, and the rate is f_EA(plaintext). I tried to make the zero event depend on the key
  or the context, and it cannot reach 0.19x random. Any per-position bijection on 29 runes sends exactly one rune
  z_i to 0, so P(doublet) = P(x_i = z_i). Measured on LP-spelled Blake (18,846 runes):
  - z_i from the previous letter, best of all 812 affine rules z = u*x_{i-1} + v: 1.24%. Plain doubling is 3.2%.
  - z_i from an English running key (x + K = v or x - K = v, every v): at least 2.2%.
  - z_i from a flat key: 3.45%.

  Only a rare fixed letter gets near 0.66%. EA (0.67% in the solved LP text) and IA (0.53%) are the candidates. A
  key-driven null rule ("the key says insert a repeat") would need a 28-rune plaintext alphabet plus a null rate set
  by hand, which is two contraptions. So I kept EA and disclosed it.
- **Target 8 (prime short clauses).** The ciphertext's clause GP sums are pseudo-random. Getting a third of short
  clauses prime would need a per-clause adjustment (pad or check rune) with its own rule. Such a rule makes every
  clause prime, not a third. It is unhintable at the right rate, so I left it unhit.
- **Target 7 (lag-5 inside words).** It would need a 5-cycle key restarted in every word, which has no tie to the rest
  of the design. Left unhit.
- **Clause-level order.** Clause breaks are kept. The unsolved clause-length lag-1 (-0.10) is not reproduced or
  tested here.

## Parameters (counted Mr Annoying's way)

| # | Choice | Kind | Decryptor must guess? | Natural or tuned |
|---|---|---|---|---|
| 1 | LP digraph spelling | structural | no | natural (Cicada's habit) |
| 2 | Numbering 1..29, so EA = 0 | structural | fixed by hint | **tuned to target 1**: EA chosen because its LP-spelling rate (0.67%) is the unsolved zero rate. It is the README's pass-through finding, not a free discovery |
| 3 | Inner operation = multiplication (0-fixing) | structural | fixed by hint | tuned: it is what makes EA, and only EA, a doublet |
| 4 | Key source = solved LP plaintext, page order | structural | fixed by hint (2-3 bits among candidate books) | natural (Cicada keyed 2012 puzzles with books) |
| 5 | Key transform = running GP sum mod 29 | structural | fixed by hint | **tuned**: needed for a flat d stream; also what defeats the known-stream attack |
| 6 | Zero key values passed over | structural | fixed by hint | forced |
| 7 | Key waits on EA | structural | fixed by hint | natural (solved-page convention); invisible except in key alignment |
| 8 | Ciphertext autokey, continuous, no restarts | structural | fixed by hint | natural; no LP precedent |
| 9 | Word lengths transposed inside clauses by key order | structural | fixed by hint | **tuned to targets 2 and 6** |
| 10 | Sort ascending, ties to the earlier word | structural | yes, 4 options | natural |
| 11 | Clause breaks kept | structural | no | natural |
| 12 | c_{-1} = 0 | numeric | barely (one rune) | natural |
| 13 | book offset = 0 | numeric | fixed by hint ("from the start") | natural |
| 14 | f_EA of the plaintext (1.00%) | hidden lever | no | **sets the doublet rate directly**; not tuned here (natural text; references 0.67-0.88%) |
| 15 | Plaintext line lengths | hidden lever | no | sets target 9; I wrote sentence-length lines |

So: 11 structural choices, 2 numeric parameters, 2 plaintext levers. Secret key: about 0 bits once the hint names the
book; without the hint, the book is one of a handful of Cicada texts (2-3 bits). The cost is in recognising the
construction. Search cost with the hint: 4 sort variants x 2 for c_{-1}, read by eye. Complexity: three operations
(multiply, autokey, transposition) plus a derived key. That is heavier than any single solved LP cipher (atbash,
Vigenere DIVINITY with skips, totient shift), and heavier than round 1, which had two operations. Each layer pays for
one target family, as listed above.

## Why the round-1 attack fails

The round-1 attack was: d = c_i - c_{i-1} has a zero shortage, so assume autokey over a 0-fixing layer, then divide
d by known streams and look for English IoC.
- Its first step still works on round 2: d is flat except at 0. A solver will correctly infer autokey over a 0-fixing
  layer, with EA = 0 if they try the rotation.
- Its second step fails. Part B of the self-check gives the attacker the right numbering and tries primes, totients,
  naturals, Fibonacci, squares, triangular numbers and prime gaps, at offsets 0-3000. Indexing is by every rune or by
  nonzero d only, and the operations are multiply by k, multiply by k^-1, and subtract k. The best IoC is 1.045-1.057.
  Three random control streams give 1.053-1.055, so all of these are at control level. The naive book attack (the
  solved LP plaintext as multiplier, either as rune numbers or as GP values) gives 1.050-1.052, also control level.
  Only the true key (the running GP sum) gives 1.865.
- The round-1 Solver's own scripts, run unchanged on this ciphertext (`round1_scripts_output.txt`), top out at 1.079,
  against 2.34 in round 1.
- Most likely route to a break: guessing "book-derived key" and trying cumulative transforms of the solved text, or a
  two-sided running-key attack. K_t - K_{t-1} = GP(B_t) mod 29 is English, so a crib in the plaintext yields book
  letters (non-uniquely: GP mod 29 is not one-to-one). The doublets also reveal where every plaintext EA is.

## Answers to Mr Annoying's round-1 required changes

1. **Spelling.** LP digraph spelling is used: THE is ᚦᛖ. The word-length result is reported as it is: mean 3.64, 2-rune
   share .267, chi2 109 on 9 df against the unsolved shape. Per the coordinator, target 5 is soft, and the cipher does
   not change any clause's length multiset.
2. **Doublet claim.** The doublet rate equals f_EA(plaintext), by construction. Expected rate on reference corpora in
   LP spelling: solved LP plaintext 0.67%, Blake MHH 0.88%, all Blake 0.86%. This plaintext has 1.00%, which is why
   target 1's rate is only marginal (z +2.2). It is listed as a hidden lever, row 14. What the cipher itself adds is
   the equal in/across-gap rate and the random places; those hold for any plaintext.
3. **Precedents.**
   - The EA rule is not the solved pages' F rule. It shares the "key waits" convention, but EA is not visible as ᛠ:
     under the autokey it shows as a repeat of the previous rune.
   - The solved key stream was phi(p) = p - 1 used as a shift. Nothing here is a solved-page precedent except
     Vigenere-style keyed shifting in general and a key that pauses.
   - Books as keys are a 2012 Cicada precedent (book codes), not an LP one.
   - Multiplication mod 29, ciphertext autokey, the running-sum key and the length transposition are all new.
4. **Honest table.** Above. It includes the marginal rows (1 rate, 3, 11), says target 9 comes from the plaintext,
   credits target 3 to the autokey, and lists the misses (5 soft, 7, 8).
5. **Hint.** The hint names the operation (multiply), the key and its transform, the zero-skip, the key-advance rule
   (waits on EA), the chain and the break rule. What it leaves open is listed in the hint section.
6. **Parameter count.** 11 structural + 2 numeric + 2 plaintext levers, in the table above.

## Files

`encrypt.py` (writes `plaintext_runes.*`, `plaintext_runes_latin.txt` and `round2/ciphertext.*`); `decrypt.py`
(writes `decrypted_runes.json` and the check); `key.txt`; `selfcheck.py` -> `selfcheck_output.txt` (about 2 minutes);
`round1_scripts_output.txt`; `plaintext.txt`.
