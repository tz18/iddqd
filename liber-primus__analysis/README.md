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
