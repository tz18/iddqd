# Round 1 cipher: "F is not encrypted, multiply by the primes, add the previous rune"

## Method

1. **Spelling: letter by letter.** Each Latin letter becomes one rune. TH, NG, EA, EO, OE, AE and IA/IO are written as
   two runes, never as the digraph runes. K->C, Q->C W, V->U, Z->S. Punctuation is dropped. Each non-empty line is a
   clause, headings included. The result is 81 clauses, 602 words and 2,448 runes (`plaintext_runes.json`).
   Why: target 5. The unsolved pages have a 2-rune word share of .155. English in LP digraph spelling gives ~.24, but
   letter-by-letter spelling gives ~.16 (.164 here). This choice is the only lever on word lengths.
2. **Inner layer: multiply by the primes, with F not encrypted.** x_i is the rune index (F = 0). Then
   y_i = x_i * k_i mod 29, where k_i = (i-th prime) mod 29 over the primes 2, 3, 5, 7, 11, ... 29 is passed over
   because it is 0 mod 29. The index i counts every rune of the text. Multiplication permutes the 28 nonzero
   residues, so F (0) is the only rune it leaves alone. That is the solved pages' "F is not encrypted" in a form
   that needs no exception rule.
3. **Outer layer: ciphertext autokey.** c_i = c_{i-1} + y_i mod 29, with c_{-1} = 0. It runs through the whole text
   without restarts.
4. **Layout.** The plaintext's word and clause breaks are shown unchanged.

**Decryption** (`decrypt.py`): y_i = c_i - c_{i-1}, then x_i = y_i * k_i^27 mod 29, using the inverse k^-1 = k^27
because 29 is prime. There are no encryptor choices to recover: the only inputs are the ciphertext, the prime
sequence and two constants. Check: `decrypt.py` reproduces `plaintext_runes.json` exactly (81 clauses, 602 words,
2,448 runes, 0 differences; `decrypt_check.txt`).

## What it is meant to reproduce, and how

| # | Target | Result | Mechanism |
|---|---|---|---|
| 1 | Doublet deficit | partly | A doublet occurs exactly when y_i = 0, which means plaintext F. The doublet rate equals F's frequency, 1.27% here, against 3.45% for random runes. It is about twice the unsolved 0.66%, roughly 2.6 SE high on 2,447 pairs. No letter-by-letter English letter sits near 0.66%: the rarest common ones (P, B, G, F) are 1.1-1.3%, and X is 0.1%. |
| 3 | Flat frequencies | yes | Autokey with an aperiodic multiplier gives chi2 32.5 on 28 df, mean GP 51.2 +/- 0.7. |
| 4 | F at the flat level | yes | F no longer passes through at the ciphertext level: 3.64% +/- 0.38. |
| 5 | Word lengths | roughly | Letter spelling gives a 2-rune share of .164 (.155 target). The mean is 4.07 against 4.47 because this plaintext's words are short, and 4-rune words are overrepresented. |
| 9 | Clause lengths | yes | Clauses are the plaintext's sentences. |
| 10 | No periodic key | yes | The primes are aperiodic mod 29, so neither c nor d = c_i - c_{i-1} has a period in 1-100 (best z +2.1 / +2.3, p 0.75 / 0.58 against shuffles). |
| 11 | No pass-through rune | yes | No ciphertext rune is over-represented. The only trace is d = 0 (F), which is the doublet deficit itself, as in the unsolved stream. |
| 12 | Exact repeats | yes (chance) | The longest repeat is 5 runes, once. |

## What it does not reproduce

- **2, doublet positions.** Doublets sit where F sits: word-initial in FOR, FROM, FEAR and FADE, word-final in OF and
  SELF. Here that is 48/32/19% first/middle/last (chi2 9.7 on 2 df), and the across-gap doublet rate is 2.5%. The
  unsolved pages have random positions and 0.79% across gaps. This is the main fingerprint against any "one
  plaintext letter -> 0" model, mine included.
- **6, word-length order.** The breaks are English breaks, so the lag-1 correlation is -0.18 and clause-final words
  average 5.3 runes. The unsolved values are -0.015 and 4.2.
- **7, lag-5 excess inside words.** No mechanism produces it. The measured 5.1% +/- 1.3 (z +1.4) is chance and is
  compatible with both 4.9% and the 3.5% baseline.
- **8, prime short-clause sums.** No mechanism produces this either: 8 of 42 (19%) against a shuffle null of 6.1.
  Getting it would need a per-clause adjustment that the cipher would then have to account for. I left it out on
  purpose.

## Parameters and key size

- **Structural choices (4).** Letter spelling; multiplication, not addition, as the inner layer; ciphertext autokey;
  the key index advancing on every rune with one continuous chain.
- **Numeric parameters (3), all at their natural value.** zero_rune = 0 (F), iv = 0, prime_offset = 0 (start at 2).
- **Secret key: effectively none** once "primes" is named. Searching the stated parameter ranges anyway gives
  29 (zero rune) x 29 (IV) x a few thousand offsets, about 2^20. The IV affects only the first rune.

**Weakness Mr Annoying will raise.** The repository's `full_model_harness.py` already tests this exact family on the
unsolved pages: shift a rare letter to 0, multiply mod 29 by a stream such as the primes, then ciphertext autokey.
Every candidate scored at noise. A solver with that harness can break this ciphertext at once. So this round is a
statistical stand-in, not a candidate for the real pages: it shows how far a three-line, Cicada-grade cipher gets
(targets 3, 4, 9, 10, 11, 12, roughly 5, half of 1) and which targets need something more (2, 6, 7, 8).

## How Cicada would hint it

Each element already has a solved-page precedent:
- "F is not encrypted": on the DIVINITY and totient pages, F was left in the clear.
- "The primes are sacred": the totient page's key was the primes.
- "Each rune carries what came before" or "the key is all around you": for the running-sum chaining.

A one-line hint like "THE PRIMES ARE SACRED. EACH RUNE CARRIES WHAT CAME BEFORE. F IS NOT ENCRYPTED" fixes every
parameter.
