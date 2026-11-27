# Round 1: Solver report

Ciphertext: 2,448 runes, 602 words, 81 clauses (`round1/ciphertext.json`).
Unsolved pages: 12,956 runes, 2,896 words, 168 clauses (`lp_common.UNS`).

**Result: the ciphertext is fully decrypted.** The decryption is in `solver_decryption.txt` (81 lines, readable
English). Re-encrypting it reproduces all 2,448 ciphertext runes exactly. The method is in section 3.

## 1. The brief's findings, measured on round 1

Uncertainty: each statistic was also computed on 400 random contiguous, clause-aligned blocks of the unsolved pages
with the same number of words (602). "Block sd" is the spread at this sample size, and z = (round 1 − block mean) / block
sd. Exact binomial or Poisson p-values are given where they are clearer. Script: `solver_scripts/compare.py`, output
in `solver_scripts/compare_output.txt`.

| # | Finding | Unsolved | Round 1 | Block sd (602 words) | Match? |
|---|---|---|---|---|---|
| 1 | Doublets overall | 0.66% (86) | **1.27% (31)** | 0.16% | **No**: z +3.8; Poisson p = 0.0007 |
| 1 | Doublets inside words | 0.63% | 0.87% (16/1846) | 0.17% | Yes (z +1.4, p = 0.13) |
| 1 | Doublets across word gaps | 0.79% | **2.50% (15/601)** | 0.38% | **No**: z +4.5, p = 0.0001 |
| 1 | Share of doublets that straddle a gap | 27% (23/86); 22% of pairs are at gaps | **48% (15/31)**; 25% of pairs are at gaps | | **No**: p = 0.003 |
| 2 | Place inside words (pair at start / middle / end; 2-rune word counted as start) | 19 / 52 / 29%; random places 28 / 49 / 24% | 12 / 62 / 25% (n = 16); random 31 / 42 / 26% | ±16% | Not testable (16 doublets). See §2: they sit where plaintext F sits |
| 3 | Rune frequencies, chi2 (28 df) | 26.4 | 32.5 (p = 0.25) | 7.6 | Yes |
| 3 | Mean GP value per rune | 51.57 | 51.17 | 0.27 | Yes (z −1.5) |
| 3 | IoC | 1.000 | 1.002 | 0.003 | Yes |
| 4 | F share | 3.54% | 3.64% | 0.37% | Yes |
| 5 | Word lengths 1..9, 10+ | .029 .155 .249 .177 .109 .088 .075 .054 .027 .038 | .035 .164 .266 **.226** .093 .096 .065 **.022** .018 **.015** | ±.006–.012 | **No**: 4-rune z +4.8, 8-rune z −4.0, 10+ z −4.6 |
| 5 | Mean word length | 4.47 | **4.07** | 0.064 | **No** (z −6.3) |
| 6 | Word-length lag-1 correlation | −0.009 | **−0.183** | 0.046 | **No** (z −3.8; English-like) |
| 6 | Clause-final word length | 4.24 | **5.32** | 0.21 | **No** (z +5.0; English-like) |
| 6 | (extra) Clause-first word length | 4.44 | **3.14** | 0.26 | **No** (z −5.1) |
| 7 | Same rune 5 apart inside a word | 4.94% (z +3.7) | 5.09% (14/275) | 0.71% | Consistent, but too few pairs to tell: p = 0.10 against flat 3.45%, p = 0.63 against 4.9% |
| 7 | Same rune 5 apart across gaps | 3.46% | 3.23% | 0.28% | Yes |
| 7 | Other within-word lags (2, 3, 4, 6) | 3.5, 3.7, 4.1, 2.5% | 2.4, 3.1, 5.2, 2.8% | 0.5–0.8% | Lag 2 low (z −2.4), lag 4 high (z +1.8); others match |
| 8 | Short clauses (≤31 runes) with prime GP sum | 18/54 (33%) | **8/42 (19%)** | | **No**: p = 0.03 against 33%; chance level (~15%) |
| 9 | Clause lengths | mean 17.2 words, sd 16.3, 2 one-word clauses | **mean 7.4 words, sd 3.7**, 0 one-word clauses | mean ±2.6, sd ±5.2 | **No**: clauses are short and uniform (z −4.0 for the mean) |
| 10 | Periodic key, periods 1–100, raw and after autokey removal | none | none (no period 1–2000 above chance, raw, difference or sum stream) | | Yes |
| 11 | Pass-through rune | none | none | | Yes |
| 12 | Longest exact repeat | 6 runes in 12,956 | 5 runes in 2,448 (one; 5 repeated 4-grams, ~4 expected) | | Yes (chance level) |

**Findings the ciphertext fails to reproduce:** 1 (overall and across-gap doublet rates, and the share of doublets
at gaps), 5 (word-length shape and mean), 6 (word-length order and clause-final length), 8 (prime short clauses) and
9 (clause lengths). Findings 3, 4, 10, 11 and 12 match. Finding 2 is untestable with 16 doublets. Finding 7 is
consistent but underpowered: a 5.1% rate on 275 pairs cannot be told apart from either 3.45% or 4.9%.

## 2. Other differences found

1. **Doublets come from one plaintext letter.** Inside words, the differences c[i] − c[i−1] are flat except at 0, so
   the doublet shortage is the only structure (in-word difference chi2 64, of which 36 comes from the zero bin; the
   other 28 bins give chi2 28). After decryption, every doublet sits on a plaintext F and every plaintext F makes a
   doublet: there are 31 of each. The brief says the unsolved doublets sit at random places, "not where any one
   plaintext letter would sit". Round 1 shows exactly that signature: doublets are concentrated at gaps (word-initial F),
   and 9 of the 31 fall in a 200-rune stretch (runes 951–1149) where the text uses F-heavy words. That stretch has a
   local rate of 4.5% against 1.0% elsewhere (Poisson p ≈ 0.002).
2. **Across-gap doublets are not suppressed.** The unsolved pages suppress doublets about equally inside words (0.18× random)
   and across gaps (0.23×). Round 1 gives 0.25× inside and 0.72× across.
3. **The word lengths are English spelled letter by letter.** The 2-rune share of .164 matches the brief's letter-by-letter
   reference (~.16) and not LP spelling (~.24). The decryption confirms it: the plaintext uses none of the digraph runes
   (TH, NG, EA, EO, OE, AE, IA), and "the" is three runes.
4. **The clauses are much shorter and more regular.** There are 81 clauses for 602 words (7.4 words per clause, sd 3.7).
   A same-size block of the unsolved pages has about 35 clauses (17 words, sd 16). Round 1 has 42 short clauses (≤31 runes)
   where a block has about 11. Clause-first runes have IoC 1.18 (n = 81, z ≈ 2), which is weak and probably chance.
5. **Lag-2/3 equalities move from inside words to across gaps.** Inside words the lag-2 rate is 0.69× random
   (z −2.1). Pairs spanning one gap are 1.43× at lag 2 (z +2.7) and 1.28× at lag 3 (z +2.0). The unsolved pages are
   flat at these lags (0.97–1.08×). Output: `solver_scripts/lag_by_gaps_output.txt`. This is moderate evidence only.
6. **The difference stream decrypts.** Once the right multiplier stream is divided out of the round-1 differences, the
   result is English (IoC ~1.8). The same attack on the unsolved pages, for every section and page, with offsets
   0–2999 and both related streams, gives nothing above the shuffled control (best IoC 1.08 against a control of 1.04,
   for units of 200 runes or more). Script: `solver_scripts/apply_to_unsolved.py`.

## 3. Decryption attempts and result

Attacks that failed, which ruled out simple families:
- Period scans 1–2000 (pooled column IoC) on the raw, difference (c[i] − c[i−1]) and sum streams: nothing above the
  look-elsewhere level.
- Linear filters a0·c[i] + a1·c[i−1] + a2·c[i−2] for all coefficients, on a continuous stream or restarted per word or
  per clause: best IoC 1.02.
- Ciphertext autokey at every lag 1–999, ± and with all a·c[i] + b·c[i−L]: nothing.
- Additive known streams (primes, totients, Fibonacci, naturals, squares, triangular numbers, prime gaps) at offsets
  0–30,000, either continuous or restarted per clause: best IoC 1.017.
- LP text as a running key (all LP runes, solved plaintext, reversed, as GP values) at every offset: best IoC 1.02.
  An English running key would give about 1.06, which the flat 1.002 already rules out.
- Conditional IoC (alphabet chosen by the previous rune, position in word, word length, clause, word index mod m):
  nothing. Kasiski: repeats at chance level. Pair equality inside one word is below chance (0.69), which rules out
  any per-word substitution (a per-word substitution would keep English's within-word repeats).

The attack that worked:
1. The in-word difference histogram is flat except for a strong shortage at 0, and no context makes the differences
   non-flat. Together that points to ciphertext autokey over an inner layer that keeps 0 fixed, with a key that changes
   every rune: d[i] = c[i] − c[i−1] = f_k(p[i]) with f_k(0) = 0, such as multiplication or a power. A doublet then
   needs plaintext F.
2. I searched known streams for k, with p = d · k⁻¹ (and p = d^(1/k)). The streams were primes, totients, naturals and
   Fibonacci, indexed by the global rune index, by in-word position count, or by word index, at offsets 0–6,000. One
   setting gave IoC 2.34 on the in-word runes, against at most 1.14 for everything else. It read as English at once.
3. The first clause decoded wrongly at one position, where the stream value was 0 mod 29. That showed the stream leaves
   out the one value that would be 0, which puts the stream one place later from there on. With that fixed, the whole
   text decrypts, including word-initial runes, with the chain starting from 0.
4. Check: re-encrypting the plaintext reproduces the ciphertext exactly (`solver_scripts/decrypt.py` checks this).

Key size and free choices: none beyond the choice of a public number sequence. The key is a short rule (a well-known
sequence, used from its start, with one value left out), and there are no per-word or per-clause choices. Word and
clause breaks are copied from the plaintext and do not affect the key. The plaintext is spelled letter by letter, with
V written U and K written C.

Run `python3 solver_scripts/decrypt.py [outfile]` from `round1/` to decrypt.
