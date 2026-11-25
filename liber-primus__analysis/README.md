# Liber Primus analysis scripts

Run from this folder (they read `../liber-primus__explorer/data/lp.json`).
Words and clauses follow the transcription's separators. A word gap is `-`, a
clause end is `.`, and a line break does not end a word. "Unsolved" means
`$`-segments 7–15.

- `clause_sums.py`: ciphertext GP sums of clauses, primality and divisibility
  tests, each checked against runes shuffled between clauses.
- `doublets_and_sequences.py`: doublet rates inside words and across word gaps.
  Also checks whether word sums look like random-rune sums (per-length
  probability check), whether they fall in candidate sets (primes, Fibonacci,
  the page-32 square) more than chance, and whether they follow
  Fibonacci-style recurrences mod 3301.
- `two_populations.py`: one- versus two-group mixture models (rune counts, and
  transitions inside words), compared with shuffled controls. Also checks
  whether rune frequencies and doublets vary from page to page.
- `transitions.py`: the rune-to-rune transition matrix (`transitions.json`) and
  its fit to the model "no self-transitions, otherwise proportional to rune
  frequency".
- `rune-transitions.html`: the state-machine diagram and heatmap.
- `doublet_positions.py`: where doublets fall. Checks position mod m (2–60),
  the gaps between doublets, and whether they sit at line breaks, word gaps or
  in particular segments.
- `isomorphs_autokey.py`: isomorph counts compared with shuffles that keep rune
  frequencies and the doublet shortage. Also checks the ciphertext-autokey
  difference streams c[i] − c[i−k] for k = 1–40 (IoC, periodic columns, and
  after removing prime, totient and Fibonacci streams).
- `long_isomorph.py`: the 17-rune isomorph on pages 27/67 and how often
  shuffled text produces one.
- `rune_selection.py`: rune-level chaffing. Checks the IoC of runes picked by
  position rules (mod m, primes, Fibonacci, squares, word starts and ends), and
  solved-text word sums used as positions or keys.
- `progressive_key.py`: rotor-style keys that step by a constant. Compares the unsolved ciphertext differences with plaintext differences from the published translations.
- `exponent_cipher.py`: "e seeks d". Tries exponent (c^(1/e) mod 29) and multiplier (c/e mod 29) ciphers where e comes from varying streams: previous rune, primes, word GP sums, solved-text word sums.
- `rsa_modes.py`: an RSA-style exponent permutation on single runes, chained like CBC/CFB, for every valid exponent. Gives each one's predicted doublet rate on English and the IoC of its decryption.
- `fixed_zero_layers.py`: ciphertext autokey over an inner layer that keeps 0 fixed (multiply by a key, or raise to a power). Undone with d = c[i] − c[i−1], then divide by the key or take the root.
- `rotate_vig13_autokey.py`: shift so EA becomes F, then a period-13 Vigenère that skips F, then ciphertext autokey. Checks the column IoC of the autokey-removed stream with zeros dropped, for periods 1–40.
- `pages_54_55.py`: the period-13 test on single page pairs, under all three page numberings, compared with every other page pair and with shuffles.
- `solve_p69_70.py`: solves the period-13 key on pages 69–70 (unsolved-folder images 54–55) by frequency fitting, in mod-29 and mod-28 versions, and prints the decryption.
- `pair_parity.py`: a Playfair-style pair test that tolerates skipped runes. Takes each rune (or none) as an unencrypted skip symbol and checks whether gaps between doublets are even.
- `exact_repeats.py`: exact repeated rune sequences (which the isomorph search skipped). Finds ᛞᛄᚢ·ᛒᛖᛁ (DJU BEI) on p42 and p70.
- `repeated_words.py`: where DJU BEI sits in its sections, and whether whole words or adjacent word pairs repeat more than chance.
- `crib_djubei.py`: cribs DJU BEI. Searches key-stream families (any offset, three position systems, either sign, with or without atbash) for settings that decrypt both copies to real words; lists implied keys for common 3+3 phrases; checks running keys from the solved translations.
- `crib_djubei_mul_exp.py`: DJU BEI cribs under multiplicative (c = p·k) and exponent (c = p^k mod 29) ciphers; searches for a constant key; compares GP sums of cribs with the ciphertext words.
- `convolution.py`: tries every short linear filter mod 29 (kernels up to length 4, which covers plain and recursive convolutions such as autokey) to see whether any recovers English-like text. Includes a check that it does recover a filtered English sample.
- `two_d.py`: checks for 2D structure. Measures repeat rates at every distance 1–300 in reading order, repeats between runes vertically and diagonally adjacent on the printed page (from the glyph boxes), and runes per line.
- `palindromes.py`: word-length repeats, word-length isomorphs and palindromes (compared with shuffled word order); rune palindromes and reversed isomorphs (compared with shuffles that keep the doublet shortage).
- `depth_search.py`: depth search on the autokey-removed stream. Slides every unsolved page against every other (and the whole stream against itself) at every offset, counting matches; scores the best alignments under subtraction, addition, division and XOR.
- `depth_null.py`: exact binomial p-values for the depth search, with the identical search on shuffled pages as a control.
- `running_key_stats.py`: simulates an English running key (a book) on English plaintext, mod 29 and mod 28, and compares its IoC excess with the unsolved text and the autokey-removed stream.
- `totient_mask.py`: checks whether a book key hidden under a totient or prime stream would show once the stream is subtracted. Tries offsets 0–2999, three restart schemes and both signs, on the raw and autokey-removed text.
- `sim_book_totient_swap_autokey.py`: simulates book key → totient → swap F with the least frequent rune → ciphertext autokey. Reports the doublet rate it produces and whether the totient-subtraction scan would still expose the book.
- `modern_fingerprints.py`: fingerprints of non-classical sources. Checks for byte-to-rune conversion artifacts in the step values, and human-randomness signs (repeats two or three places apart, steps to the next rune in alphabet order).
- `boundary_resets.py`: checks for cipher state resets at section, page, paragraph and line starts (first-rune distribution; repeat rate across the boundary).
- `word_position.py`: rune distribution by position in the word, and at line starts.
- `line_breaks.py`: runes at line breaks that split a word. The excess (EA, M, D…) tracks glyph width (from `glyph_widths.json`), so it comes from typesetting.
- `jpeg_forensics.py`: compares JPEG encoder settings and metadata (colour mode, quantization tables, ICC profile, appended data) for solved and unsolved pages, and decodes the data appended to `05.jpg`.
- `lp2_bytes.py`: byte-level comparison within the LP2 batch. Compares An End and Parable (73–74) with the 56 unsolved pages: header bytes, Huffman tables, how the image data ends, bits per pixel, and identity with the unsolved-folder copies.
- `apostrophes.py` (output `apostrophes.json`): finds apostrophe and quote marks in the scans, which the transcription omits. The unsolved text has 4 in-word apostrophes, contractions shaped 3+1 or 2+1 (DON'T on solved p12 confirms the convention), and 9 quote marks.
- `edit_traces.py`, `edit_gaps.py`: look for traces of post-layout edits (spacing, alignment, glyph shape, gaps between runes). Gaps are 0–8 px throughout, with no traces of edits.
- `zero_key_ciphers.py`: modern ciphers with all-zero keys, used (a) as keystream generators mod 29 or 28 on the raw and autokey-removed text, and (b) as decryption of the runes encoded as bytes. The only highlights come from IDEA and DES, whose all-zero keys are known weak keys.
- `wisdom_key.py`: uses the identical 3,368-byte `wisdom`/`folly` files from the 2013 CicadaOS disc (`2013/02/3301.iso`, `/tmp` in its boot image) as a key. Tries six rune conversions at every offset, applied cyclically or restarting each section, to the raw, autokey-removed and mod-28 text, plus hash-derived AES/ChaCha20 keystreams. Nothing scored above noise (max IoC 1.004).
- `cicadaos_pad_check.py`: reproduces the 2013 use of the CicadaOS data file `560.13` as a one-time pad (Dataset 13, offset 12821, XOR → `gbyh7znm6c7ezsmr.onion`).
- `circumference_key.py`: "shed our circumferences" / "the key is all around you" as keys. Tries the page ring as key for the interior (every start and direction), word first/last runes, and π / 2π digits (base 10 and base 29) as running keys. Nothing above noise.
- `full_model_harness.py`: runs candidate keystreams through the full model (shift a rare letter to 0, an inner layer that keeps 0 fixed, ciphertext autokey). Inner layer is a mod-28 shift or multiplication mod 29; the key advances on every rune or skips zeros; offsets and restarts are scanned. A self-test on simulated English recovers IoC 1.75 and reproduces a 0.62% doublet rate. Candidates tried: primes, totient, Fibonacci, π/2π, wisdom, zero-key AES/ChaCha20, AES keyed by SHA-256 of 19 phrases, and the page rings. All at noise.
- `word_sum_subsequences.py`: searches the word GP sums for ordered runs of consecutive terms of known sequences, with any gap or gaps of at most 50 or 20 words. Includes the page-30 square's sequence prime(F(n)+1) and its 3301-minus form. The control shuffles the word order. Best hit: Fibonacci 55, 89, 144, 233, 377 on p44–45 with gaps ≤ 50 (p = 0.002 for that test; about 0.1 after allowing for 48 tests).
- `structure_score.py`: scores peeled text by how non-random it is, using eight measures: letter and pair frequencies, column IoC for periods 2–40, repeats at distances 1–50, doublets, 5-gram repeats, compressibility. Calibrated on wrong keys. Detects a buried Vigenère layer with score 616 against 3.5 for wrong keys. Rescoring all full-model candidates with it: none exceed the control (best-of-160 for random keys reaches 5.35; best candidate 5.26).
- `retest_all.py`: reruns earlier peel tests with the structure score, each with a random-key control. Every score is saved to `results/retest_<family>.csv.gz`.
- `retest_offset0.py`: the principled subset. Wisdom conversions and the totient/prime streams starting at their beginning, either continuous or restarting per section or page, on the raw, autokey-removed and mod-28 text. Best 4.95, against random-key controls with median 4.42 and max 7.33.
- `history/`: a review of Cicada's 2012–2016 history for clues to the final layer (`history_insights.md`, written by a research agent from local copies, with sources). Includes the discovery that the first 64,167 bytes of CicadaOS `560.13` XOR `gematria-primus.jpg` give a base64 PNG of a cicada (`560_13_xor_gematria.png`), followed by "33010" filler.
- `history_hypotheses.py`, `history_hypotheses_control.py`: the history review's test ideas, run through the full model with controls. Long keys under the skip rule, pads/mp3s with "Skip" and base-29 chunking, the Valēte P.S. number, prime streams anchored at 1033/3301/1031/1229/1259 both ways, discrete-log autokey, the cicada image as a key, and periods 41–200. All at control level (best 6.97 against best-of-83 control replicates of 6.16–7.82).
- `skip_search_54_55.py`: reproduces the solvers' period-13 skip search on unsolved-folder pages 54–55 (pages 69–70 here), with controls. Without skips the period-13 column IoC is 1.379: p ≈ 0.0005 against shuffles, and the highest of 53 page pairs. Searching all pairs and periods 2–40, though, it is within chance.
- `p69_70_period13.py`: FIRFUMFERENFE and a frequency-solved period-13 key on pages 69–70, plus a per-column breakdown. No English.
- `period13_skip_model.py`: fits a period-13 key with skips by alternating best path and key estimates, on pages 68–70. Result (IoC 1.33) is within the shuffled control (max 1.35).
- `period_scan_null.py`: proper null for the period scan. Pages 69–70 at period 13 (pre-specified): z = 4.05, p = 0.0002. Searching 53 page pairs at fixed period 13: about p = 0.011. Searching all pairs and periods 2–40: z = 2.08, p = 0.055.
- `p69_70_columns.py`: per-column period-13 IoC on pages 69–70, and an odd/even contrast test. Strong columns are 2, 9, 11 and 13 (counted from the first difference). The odd/even difference is z = 0.9, not significant without skips.
- `unreasonable.py`: "do four unreasonable things each day" as irrational keys. Digits of πr/2 for 18 values of r (base 10 and 29, with and without the integer part), r per page, and the four irrationals π, e, √2, φ summed or cycled. 82 keys, all at control level (best structure 6.99 against best-of-~80 random replicates of 6.2–7.8).
- Reruns after the s+k fix (`results/rerun_add_*.txt`): nothing changes. Totient/prime with s+k scores 5.50 structure (z = 2.4 against its own best-of-160 null), chance among about 24 candidates.

## blake_wordlength_crib.py
Cipher-agnostic crib: slides every clause (>= 5 words) of Blake's *The Marriage of Heaven and Hell*
(`sources/`, the text Cicada used in 2012) along the unsolved word-length sequence, allowing EA/EO/IA/IO etc.
as one or two runes. Result: 3 hits for 5-word clauses vs 4.9 expected from shuffled word orders (p 0.77),
none for 6+ words. No sign the unsolved pages quote MHH verbatim.

## pgp_signature_key.py
The 2017-04-04 "Beware false paths" signature (`sources/pgp/`), with Cicada's key 7A35090F from keyserver.ubuntu.com.
s^e mod n is valid PKCS#1 v1.5 + SHA-512 DigestInfo, and the hash matches the clearsigned text exactly
(`'Beware false paths.  Always verify PGP signature from 7A35090F.\n\n3301\n'`): the signature is genuine and its
512 bytes are fully determined by the signing process. s is not a usable private exponent (x^(e*s) != x).
As an LP key (bytes mod 29, base-29 digits, whole packet) it scores at the random-key level.

## phrase_crib.py
Generalised word-length crib: every 4-10 word window of the solved LP text and of Cicada's signed messages
(2012-2014 archive, 2014 OutGuess messages, 2017), 2,978 windows, slid along the unsolved word lengths. Counts
match shuffled-order nulls at every k (z between -0.7 and +0.6); no match longer than 7 words. No verbatim reuse.

## base60_block_rsa.py
The base-60 block on unsolved pages 64-66: 256 pairs (alphabet 0-9A-Za-x) decode to exactly 256 bytes (max 255),
a 2048-bit number S. Tested with Cicada's two RSA-4096 keys (primary 7A35090F, subkey 671DDEB1), S big- and
little-endian: S^e mod n has no PKCS#1 or other structure (printable fraction 0.33-0.38, random is 0.37); S is
not a valid private exponent; gcd(S, n) = 1. As a modulus: small factors (2,5,43,53 / 5,14827), composite
cofactor, no close-prime Fermat factorisation, not a perfect power. As an LP key it scores at random level.
A real signature from a 4096-bit key is 4096 bits long, so a 2048-bit block cannot be one of Cicada's signatures
(chance 2^-2048); if it is a signature it is from some other, 2048-bit key.

## lp_common.py
Shared loader: every rune with page, line, column, word, clause, segment, glyph box, and the plaintext of solved
segments (workbench default ciphers and F-skips; decryption checked against the published text).

## views_calculus.py (results/views_calculus.txt)
Other "coigns of vantage" and calculus transforms, each scored with the structure battery against 40 nulls that
keep the page/line/word layout, rune frequencies and doublet rate. Views: pages rotated (read down columns, either
way), the 3D page stack (same line/column cell through all pages), acrostics (word/line/clause first and last
runes). Calculus: finite differences of order 1-3, running sums of order 1-2, formal derivative/integral over GF(29)
(c*i, c/i, i = position in page/line/word), differences and sums down columns. All 23 views at chance (best
p = 0.05 among 23) except line-first runes, which is the known typesetting effect (wide glyphs EA, M, D wrapped to
the next line when a word is split; `line_breaks.py`).

## solved_sums.py (results/solved_sums.txt)
"Book of primes": GP sums of words, clauses, lines, paragraphs, pages and sections of the solved segments, pt and
ct, vs a length-preserving shuffle null. Clause sums are prime far beyond chance in the plaintext (45 of 94, null
13.7, z 9.2); nothing at word, line, paragraph, page or section level.

## prime_clauses_channels.py (results/prime_clauses_channels.txt)
(1) The solved prime-clause effect is entirely in short (<= 31 rune) maxim-like clauses (39/59, z 11.2; long 6/35,
chance). Ciphertext of the encrypted solved sections loses it. The UNSOLVED ciphertext shows it too: short clauses
18/54 prime vs 8.3 (z 3.7, p 0.0008; robust for cutoffs 25-50 runes), not explained by parity or small factors
(18 of 22 sums coprime to 30 are prime), absent for words, lines, pages, paragraphs. Cutoff taken from the solved
pages; about six units were looked at, so treat as p ~ 0.005-0.01. One sum is 1033.
(2) Word lengths, the visible channel: English in runes (solved LP, Blake) has ~25% 2-rune words and lag-1
correlation -0.10 to -0.14; the unsolved text has 15.5% and -0.015 (shuffled 0.000 +/- 0.019). The unsolved word
breaks do not behave like English word lengths.

## prime_partitions.py (results/prime_partitions.txt)
(1) Each solved plaintext clause cut on word boundaries into consecutive all-prime pieces (fewest pieces, by
dynamic programming), with a null of the same word lengths refilled with random runes. Of 57 clauses with 6+ words,
35 can be cut (null 24.1); most of those are whole-clause primes. 22 cannot be cut at all (mostly Koan narrative
and Loss of Divinity prose), so "every phrase is prime" does not hold. (2) All 31 unsolved clauses with prime
ciphertext sums, with runes, Latin, page/lines and sum.
Word lengths: Blake spelled WITHOUT digraph runes (TH = T+H, etc.) gives 2-rune share 0.166 and 3-rune 0.230,
close to the unsolved 0.155 / 0.249; the unsolved lag-1 correlation (-0.015) is still far from English (-0.13).

## sum_preserving.py (results/sum_preserving.txt)
Tests a cipher that keeps GP sums. Word level: English reuses a few words, so for each length a few sums dominate
(2-rune words: collision rate 0.11-0.16, top-5 sums 68-71%); the unsolved ciphertext matches random runes (0.015,
14% vs 0.013, 13%), so word sums are not preserved. Clause level: a sum-preserving cipher keeps the mean GP per rune,
but English has ~45 (either spelling) and the unsolved ciphertext 51.6 +/- 0.3, so sums cannot be preserved
overall; even the 18 short prime clauses average 51.6 per rune (English expectation 45 +/- 1.9). The short clauses
are as random as the rest (unigram chi2, doublet rate).

## prime_clauses_robustness.py (results/prime_clauses_robustness.txt)
The unsolved short-clause prime excess is spread out: segments 7-11 (8/24, z 2.3) and 12-15 (10/30, z 3.1); LP1
unsolved pages 16/45 (z 3.7), LP2 unsolved pages only 9 short clauses (2/9). It holds when "short" is counted in
words (<= 5, 6 or 8 words: z 3.3-3.5). Paragraph-first short clauses are prime 6/13, others 12/41 (heading-like, small n).

## divine_keystream.py (results/divine_keystream.txt)
User's theory: prime-sum clauses are "divine", need no decryption, and are keystream for the rest. Tested: the unsolved
prime clauses (31, or the 18 short) and the solved LP prime-clause plaintext as running keys over the non-prime
clauses (3 ops, with/without F-skip, forward/reversed); each prime clause keying the clauses that follow it; the
prime sums themselves as keys (shift, multiply, decimal and base-29 digits); and the full model. Controls: keys made of
the same number of random non-prime clauses. Everything at control level (best z 1.6, p 0.07: solved LP prime
plaintext as running key). Note: the multiply control is inflated by non-prime sums divisible by 29 (key 0).

## key_bucket_test.py (results/key_bucket_test.txt)
Cipher-agnostic key test: if each key rune selects any substitution alphabet (Vigenere, Beaufort, multiplication, any
keyed 29x29 table), the ciphertext runes sharing a key rune have plaintext IoC whatever the table. Statistic: weighted
IoC within the 29 key-value buckets. Calibration with the true applied keys: Welcome 2.33 (random keys 1.18 +/- 0.09),
Koan 2 1.95 (1.13 +/- 0.14), An End 1.69 (0.90 +/- 0.5). The prime-clause keys (31 or 18 short, forward/reversed, raw or
autokey-removed, with/without F-skip) and the solved LP prime plaintext: all at control level (|z| < 2).

## passthrough_rune.py (results/passthrough_rune.txt)
Which rune passes through unencrypted? Model A: freq(X) = f_X + (1-f_X)/29; model B (encrypted runes never land on X):
freq(X) = f_X. Raw ciphertext, whole text and each section: no rune with English frequency above ~0.5% fits (F, Y, B...
strongly rejected); only the rarest (X, J, AE) are indistinguishable from "none". Autokey-removed stream: the zero
symbol (doublets) is at 0.66% +/- 0.07%, which model B fits overwhelmingly (+177 log-lik vs uniform). Runes with that
English frequency: EA 0.67% and IA 0.54% in LP spelling; in letter-by-letter spelling no rune is close (X, J 0.18%).
