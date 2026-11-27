# Solver methods (for future rounds)

These are the tests and attacks used in round 1, described as methods only. Scripts live in `round1/solver_scripts/`.
`load.py` reads a round's `ciphertext.json` and rebuilds the unsolved pages as the same clause / word / rune nesting,
so every test runs on both texts with the same code.

## A. Comparing the ciphertext with the unsolved pages

1. **Sample-size-matched uncertainty.** Compute each statistic on the ciphertext. Then compute it on about 400 random
   contiguous, clause-aligned blocks of the unsolved pages that hold the same number of words, and report z and the
   percentile against those blocks. This handles statistics with awkward variances, such as correlations, mean lengths
   and clause counts. For rates, add exact binomial or Poisson p-values (`compare.py`).
2. **Doublets, split three ways:** inside words, across word gaps, and the share of all doublets that straddle a gap,
   compared with the share of adjacent pairs that are at gaps. A cipher whose doublets come from one plaintext letter
   shows up here, because English letters are not spread evenly between word-initial and word-internal places.
   Also look at where the doublets fall along the text: clusters point to plaintext-driven doublets.
3. **Equality rate by lag and by number of gaps spanned** (`lag_by_gaps.py`): same-rune rate at distance L = 1..8,
   split into pairs inside one word, across one gap, across two, and so on. This is more telling than the lag rates
   inside words alone.
4. **Word-length shape:** the shares for 1..10+, the mean, the lag-1 correlation between neighbouring words' lengths,
   and the mean length of the first and last word of each clause. A 2-rune share near .16 rather than .24 suggests
   letter-by-letter spelling. A negative lag-1 correlation and long clause-final words suggest that the plaintext's
   word breaks have been kept.
5. **Clause statistics:** words per clause (mean and sd), one-word clauses, the number of short clauses (≤31 runes)
   and how many have a prime GP sum.
6. **Frequency tests:** chi2, mean GP value, IoC, F share, and IoC by position in the word, of the last rune, and of
   the first rune of each clause.

## B. Structural probes before attacking

1. **Difference histograms.** Histograms of c[i] − c[i−L] inside words for L = 1, 2, 3, of the same across gaps, and
   of the sums. Compute chi2 with and without the zero bin. If the only structure is a shortage of zeros, the
   difference stream is otherwise uniform.
2. **Conditional (grouped) IoC** (`condioc.py`, `zero_fixed.py`): pool same-value pairs inside groups defined by a
   context. Contexts: previous rune, rune two back, next rune, position in the word, position from the end, word
   length, (length, position), clause, word, word index mod m. Compare with the same grouping after permuting the
   contexts. Run it on the raw runes and on the in-word differences. Any substitution alphabet chosen by that context
   lifts the grouped IoC toward 1.7.
3. **Pair equality inside a unit** (`perunit.py`): the rate at which two runes, or two differences, from the same
   word or clause are equal. A per-word bijective substitution keeps the plaintext's within-word equalities, so a rate
   below chance rules it out.
4. **Deconvolution of key steps** (`deconv.py`): if c = p + k, the in-word cipher differences are the plaintext
   differences convolved with the key-step distribution. Estimate the step distribution by EM, using the in-word
   difference distribution of the solved LP plaintext. Check the likelihood gain against a uniform step distribution.
5. **Windowed IoC and doublet counts** (150-rune windows), to look for locally constant or locally weak keys.

## C. Attack families tried

1. **Periodic keys at long periods** (`longperiod.py`): the pooled same-rune count at distances that are multiples of P,
   for P = 1..2000, on the raw, difference and sum streams. Judge the maximum z against the number of periods tried.
2. **Linear filters** (`linfilter.py`): a0·c[i] + a1·c[i−1] + a2·c[i−2] mod 29, for all coefficients. Run it on a
   continuous stream and restarted per word and per clause.
3. **Ciphertext autokey at any lag** (`autokey_lags.py`): c[i] ± c[i−L] for L ≤ 999, and a·c[i] + b·c[i−L] for L ≤ 60.
4. **Additive known streams** (`streams.py`): primes, totients, p+1, Fibonacci, naturals, squares, triangular numbers
   and prime gaps, mod 29, as c − k or k − c. Index them globally at offsets up to 30,000, or restart them at each
   clause.
5. **LP text as a running key** (`lpkey.py`): the whole LP rune stream, the solved plaintext, both reversed, and their
   GP values, at every offset, as c − k and c + k. Note that an English running key on English gives an IoC of about
   1.06 (checked on the solved LP plaintext), so a flat ciphertext (1.00) already argues against it.
6. **Ciphertext autokey over an inner layer that keeps 0 fixed** (`zf_streams.py`): take d = c[i] − c[i−1]
   (optionally only inside words), then p = d · k⁻¹ or p = d^(1/k) with k drawn from known streams. Index the stream
   by the global rune index, by the in-word position count, or by the word index, at offsets up to 6,000. Mask
   positions where k is 0 mod 29, or not coprime to 28 for the power version, and score by IoC over the rest. Expect
   this family when the in-word differences are flat apart from a zero shortage. Two cautions: a key value of 0 mod 29
   would make the encryption lossy, so allow for whatever rule the encryptor used to avoid it. And look at the first few runes and the word-initial runes separately when testing whether the chain
   runs across word gaps.
7. **Kasiski** (`kasiski.py`): repeated 3- to 5-grams and whole words, with distances and in-word positions, compared
   with the number of repeats expected by chance.
8. **Cross-check on the unsolved pages** (`apply_to_unsolved.py`): run any successful attack family on each unsolved
   section and page, with a shuffled control, to see whether the round's cipher could be the unsolved one.

## D. Verifying a break

Re-encrypt the recovered plaintext with the recovered rule and check that it reproduces every ciphertext rune. Also
check that the rule leaves no free choices: the start value, how word and clause breaks are treated, and how any
zero-valued key is handled.
