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
