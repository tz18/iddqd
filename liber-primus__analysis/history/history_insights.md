# Cicada 3301 history (2012 to 2016): what it suggests about the LP's final layer

Paths used below:
- `ON` = /tmp/claude-0/-home-user-iddqd/c4d0f226-87a8-5085-be90-4aec3e9a339e/scratchpad/on
- `ISO` = /tmp/claude-0/-home-user-iddqd/c4d0f226-87a8-5085-be90-4aec3e9a339e/scratchpad/iso
- `IDDQD` = /home/user/iddqd

Each item is labelled. **[DOC]** means the docs or artifacts state it. **[VERIFIED]** means I reproduced it here. **[SPEC]** is my own speculation.

---

## 0. New findings from this session (verified locally)

1. **[VERIFIED] The first 64,167 bytes of CicadaOS `560.13` are not random.** XOR them with `IDDQD/2013/03/gematria-primus.jpg`, which is also exactly 64,167 bytes. The result is ASCII text:
   - a base64 PNG, 20,709 characters long. It decodes to a 521×523 cicada image (both sides prime), grey+alpha, with only grey levels 0–7, so it looks almost black. Its PNG tIME is 2012-12-31 23:37:39 UTC. The Twitter account @1231507051321 was created five minutes earlier, at 23:32:20 (see `ON/2014/01.twitter/twitter_posts.json`, user.created_at).
   - then a line of dashes.
   - then the filler `33010` repeated to the end, which contains both 3301 and 1033.
   - After byte 64,167 the file is incompressible (zlib ratio 1.000).
   - Saved as `found/560_13_xor_gematria.png` and `.bin` in the scratchpad. Bit planes 0–2 show only the same cicada, with no hidden text.
   - Consequences:
     - The 2013 phone offset 12821 falls inside this base64 region. So the "one-time pad" was partly built from an earlier artifact: a pad derived from a previous stage's output.
     - Cicada deliberately chains artifacts with XOR: tweets ⊕ 761.mp3 = Gematria Primus JPG, and GP JPG ⊕ 560.13 = cicada PNG.
     - `560.17` and `_560.00` showed no such structure, against ~280 local artifacts tried at offset 0, including LP pages, mp3s, the ISO files and 2012 images.
2. **[VERIFIED] The tweets ⊕ 761.MP3 relationship.** Offset 0, no skip: XORing the tweets with 761.MP3 gives `gematria-primus.jpg` byte for byte. The bot's last tweet was `Offset: 0, Skip: 0, Col: 65, Line: 988` (`twitter_posts.json`). Cicada's own pad notation therefore has two parameters, **Offset** and **Skip**. The phone calls used `Dataset:13 Offset:12821` ([DOC] `ON/2013/03.theonions/README.md`). "Skip" was never used with a non-zero value anywhere in the documented history.
3. **[VERIFIED] "The key is all around you" is a 2013 hint, not a hint for the LP.** In `ISO/initrd/usr/local/bin/message.txt` it reads `@1231507051321 / The key is all around you.` The `@` marks a Twitter handle, so the hint pointed at the tweet hex that surrounds the mp3 key. It was fully used in 2013. Facts about the handle:
   - 1231507051321 is a **palindromic prime**.
   - The Valēte image hides the palindromic primes 2 3 5 7 11 13 11 7 5 3 2 in its whitespace ([DOC] `ON/2012/03.subreddit/01.subreddit/README.md`).
   - So palindromes and mirroring are a recurring Cicada motif.
4. **[VERIFIED] "Parable 1,595,277,641" factors as 1031 × 1229 × 1259**, three primes, the same shape as 845145127 = 503 × 509 × 3301. Notes:
   - 1229 = π(10000).
   - 1031 is the twin of 1033.
   - The docs never explain this number. It is the 761.MP3 ID3 key name.
5. **[VERIFIED] prime_echo.** CicadaOS's `prime_echo` prints the 464 primes from 2 to 3301 (π(3301) = 464), 10 per line, pausing 2 s after **1033** and after **3301** (`ISO/initrd/usr/local/bin/prime_echo`). The pause marks 1033 and 3301 as anchor points within the prime stream:
   - 1033 is the 174th prime.
   - 3301 is the 464th prime.
6. **[VERIFIED] wisdom/folly timestamps.** The identical `wisdom`/`folly` files (3,368 B, entropy 7.94) were the last files added to the initrd. Their cpio mtimes are 2013-01-03 01:23:42 and 01:25:10, after message.txt.asc (00:08:46). XOR checks against all three datasets and 761.MP3 at every offset (10-byte printable test) gave only chance-level hits.
7. **[VERIFIED, negative] The datasets as LP keystreams.** I fed `_560.00`, `560.17` and `560.13` through `full_model_harness.scan`:
   - starts at 0, 12844, 20709 and 64167;
   - raw bytes, bytes<232 mod 29, and bytes<252 mod 28;
   - offsets 0–399;
   - restart none or per segment.
   
   Best IoC 1.0036, against random-byte controls of 1.0021–1.0029. This is noise. Script: `scratchpad/ds_test.py`.

---

## 1. Chronology: technique, key source, how it was signalled, conventions

### 2012 ([DOC] `ON/2012/**/README.md`)

| Stage | Technique | Key source / signal | Convention or motif |
|---|---|---|---|
| final.jpg (509×503) | Text appended after JPEG EOF: "TIBERIVS CLAVDIVS CAESAR says …" | Caesar named outright; shift −4 found from the known "http" | Hint by persona name. Image dimensions are primes, used later. |
| Duck decoy (m9sYK.jpg) | "you can't guess how to get the message out" | Pun hinting at OutGuess | Hints are puns. |
| OutGuess on final.jpg | Book code `line:char`, 76 pairs | Book = the subreddit's own text | Steganography is the main carrier throughout. |
| Subreddit a2e7j6ic78h0j | Vigenère on post titles. Key = subreddit name in base 36: a=10, 2, e=14, … (`10 2 14 7 19 6 18 12 7 8 17 0 19 7 14 18 14 19 13 0 1 2 0`) | Key given as Mayan numerals in the header and confirmed by the title | **Key = the name/label of the container.** Non-letters pass through without advancing the key (as in the solvers' script `scripts/vigenere.py`, which also resets per line; that reset may be the solvers' invention). Plaintext is the Mabinogion, *Lady of the Fountain*. |
| Book code → phone number | Mabinogion `line:char` | | |
| Phone (214) 390-9608 | "three primes associated with final.jpg … multiply" | 3301 × 509 × 503 = 845145127 | **Products of primes as identifiers.** The same shape recurs in 1595277641. |
| 845145127.com | OutGuess: "Patience is a virtue", countdown, GPS coordinates | Physical posters (14 cities) | Physical-world key delivery. |
| Whitespace page | Tabs/spaces as binary → 10 twelve-digit numbers | Not signed. In the "second chance" branch, solvers summed and factored them (1853143003544.tk → largest prime factor 33091839349.tk) | Numbers → factorisation → domain. |
| QR posters → Agrippa image | Book code on Gibson's *Agrippa*. "the product of the first two primes" = 6 | Riddle about a self-erasing poem | **Digits written as prime descriptions.** |
| Encyclopaedia image | Book code on Britannica 11th ed. vol. 6 | "How many lines of the code remained when the Mabinogion paused?" → 75 − 69 = 6, **0-indexed** | **Key derived from counting a previous stage's artifact.** 0-indexing is stated explicitly. Result `eq6emgv2eHsrix6t.onion` was never used. |
| Agrippa onion | E-mail sign-up | | |
| RSA (Crypt::RSA, OAEP) | Factor a low-bit modulus | Per-person unique key | Individual keys. "Second chance" via a .tk TXT record. |
| MIDI | Blake, *Marriage of Heaven and Hell*, "Let the Chorus be your guide" | Song key unknown in docs | |
| Valēte (503×509, flipped dimensions) | P.S. 131-digit number | **Never explained.** Composite, no small factors (verified up to 10^6) | Palindromic-prime whitespace 2..13..2. |
| Stereogram 8D7hN "Problems?" | "The key has always been right in front of your eyes" | | Keys hidden in plain sight. |

### 2013 ([DOC] `ON/2013/**/README.md`)

| Stage | Technique | Key source / signal | Convention or motif |
|---|---|---|---|
| 4chan second.jpg | OutGuess book code `chapter:verse:char` (roman chapters) on *Liber AL vel Legis* | Riddle: "a book whose study is forbidden / dictated to a beast". Bare numbers 5 and 0 appear inline | Numbers as literal digits inside book codes. "-" stands for "/" in the URL. |
| Dropbox 3301.iso (TinyCore) | Boot prints the primes to 3301, then "@1231507051321 / The key is all around you" | | Pauses at 1033 and 3301. |
| 761.mp3 "The Instar Emergence" | ID3 "Parable 1,595,277,641: … shed our own circumferences; Find the divinity within and emerge." | **The Parable text later reappears as the LP's last page.** | The 2013 artifact refers forward to the LP. |
| Twitter @1231507051321 | 988 hex tweets (xxd style) ⊕ 761.mp3 (offset 0) → gematria-primus.jpg | Account name in message.txt | **Pad = an mp3 file. Notation "Offset/Skip".** |
| Gematria Primus JPG | OutGuess whitespace → `emiwp4muu2ktwknf.onion` | | First appearance of the rune/prime table. |
| (hidden) GP JPG ⊕ 560.13 | base64 cicada PNG + 33010 filler (finding 0.1) | | |
| Onion 1 | "Web browsers are useless here" → telnet | | |
| Onion 2 | "knock on the sky and listen to the sound" → ping payloads | | Data hidden in protocol metadata. |
| Onion 3 → posters | Phones ending 3301/1033. Access code had to be **gematrified** (runes → GP values) | Physical posters | **Gematria conversion as an input step.** |
| Phone | `Dataset:13 Offset:12821 Data:<hex>` ⊕ 560.13 → onion (one per poster) | CicadaOS data files | **Pads with offsets. Each person or place gets a different offset.** |
| SSSS | Shamir shares, 5 of 10 | | Secret split across locations. |
| Leaked test | Q4 "**You cannot step into the same river twice.**"; Q14 "I am the voice inside my head" (later LP Koan 2); Q3 "addition is modeled after what?" | | The questions mirror LP themes. |
| Leaked server spec | Commands RAND, QUINE, **BASE29** ("BASE29 3301 → 3QO"), CODE, **KOAN**, **DH [p]**, NEXT | | Base 29 and koans appear before the LP. A Diffie–Hellman exchange (modular exponentiation) is part of the curriculum. |

### 2014 ([DOC] `ON/2014/liber_primus/pages/README.md`, `IDDQD/lp_outguessed/`)

- LP pages 00–02 carry single hex bytes `fe`, `57`, `a3` in OutGuess (signed).
  - Page 03 holds a hex-dumped JPEG ending `814fc7fe637fffd9`, plus "Let the text guide you."
  - I decoded the JPEG as **runes mixed with digits**: an onion address written in runes (`found/lp03.jpg`).
  - **Convention: runes and digits mixed, transliterated via the GP.** The role of the three single bytes fe/57/a3 is not documented.
- Page 08: "For those who have fallen behind" is a pair-grid transposition (two rows of letter pairs). I did not finish decoding it.
- Pages 10–13: "Create one Tor hidden service … three magic squares".
  - The 3-filled template with 310/12/103 is shown in versions filled with 3, 0 and 1.
  - **3301/1033 mirroring again.**
- Solved LP:
  - Section ciphers (`IDDQD/liber-primus__keys/liber-primus__keys.txt`): atbash, atbash+3, DIVINITY and FIRFUMFERENFE Vigenère with **F skipped and the key not advancing**, and φ(prime) with F skipped.
  - Text says "THE PRIMES ARE SACRED / THE TOTIENT FUNCTION IS SACRED / ALL THINGS SHOULD BE ENCRYPTED".
  - Page 1 warns "DO NOT EDIT OR CHANGE THIS BOOK … EITHER THE WORDS OR THEIR NUMBERS".
- 2014/05 "Interconnectedness.mp3": its ID3 holds title and artist only (verified with ffprobe). No hidden text was checked beyond that.

### 2015–2016

- Tweet of 2015-07-28 → pastebin smRatr3D. The content is not stored locally.
- Tweet of 2016-01-06 → `4gq25.jpg` ([DOC] twitter_posts.json; the file is in `IDDQD/2016/01`). Its OutGuess payload is the "Liber Primus is the way. Its words are the map, their meaning is the road, and their numbers are the direction…" message.
  - **[UNVERIFIED]** I could not confirm the exact text: there is no OutGuess binary here, and building one was blocked.
  - No signed-message file exists in `IDDQD/2016/01`; only the jpg is there.

---

## 2. How Cicada builds and hands out keys

1. **Keys are labels of the thing you are looking at.** Examples:
   - the subreddit name was the Vigenère key;
   - "DIVINITY" and "FIRFUMFERENFE" come from the text;
   - the image dimensions were factors of the domain;
   - the @handle points to the pad.
2. **Keys come from counting or indexing earlier artifacts.** Examples: Mabinogion lines remaining = 6, 0-indexed; book codes over the subreddit text, *Agrippa*, *Liber AL*, Britannica.
3. **XOR pads are whole files.**
   - Pads used so far: 761.mp3 (tweets) and 560.13 (phone data).
   - 560.13 is itself partly another artifact XOR text.
   - Parameters: dataset number, offset and (unused) skip.
   - Different solvers or locations get different offsets.
4. **Number motifs.**
   - Primes, products of primes, palindromic primes.
   - 3301 and its reverse 1033 as markers (pauses in prime_echo, phone numbers, the 1033.jpg cover, magic-square templates, the `33010` filler).
   - The totient. Base 29 (server spec).
5. **Delivery.**
   - Steganography: OutGuess, whitespace, appended data, ID3, ping payloads.
   - Physical posters, phone calls, Twitter bots.
   - The posted riddles were self-contained. Plaintext style moved from public-domain books to Cicada's own texts in the LP.
6. **Skip-a-symbol conventions.**
   - Non-letters pass through the subreddit Vigenère.
   - F passes unencrypted with the key frozen in the LP Vigenère and in An End.

### Never used or never explained

| Item | Source |
|---|---|
| Valēte P.S. 131-digit number | `ON/2012/03.subreddit/01.subreddit/README.md` |
| `eq6emgv2eHsrix6t.onion` | 2012 book code 2 |
| The "Parable 1,595,277,641" number | 761.mp3 ID3 |
| `_560.00` and `560.17` (unused datasets, about 4 MB and 1.2 MB). The underscore prefix on `_560.00` is unexplained. | ISO |
| wisdom/folly and the empty `aberr`. **Correction:** `aberr` is a standard TinyCore file, not Cicada's. | initrd/tmp |
| The "Skip" field of the tweet signature line | twitter_posts.json |
| LP OutGuess bytes fe/57/a3 on pages 00–02 | `IDDQD/lp_outguessed` |
| 1231507051321 as a number beyond being a handle | |
| Pastebin smRatr3D (2015) | |
| Interconnectedness.mp3 (no analysis in docs) | |

---

## 3. Specific questions

- **(a) A final step that suppresses doublets.** Nothing in 2012–2014 shows a ciphertext-autokey step explicitly.
  - [SPEC] The closest thematic hints:
    - leaked test Q4 "You cannot step into the same river twice", which reads naturally as "the same rune never follows itself";
    - the 2013 server's **DH [p]** and the RSA stages, which show Cicada likes chained modular arithmetic;
    - the LP's "F is skipped and the key does not advance" convention. That convention means one plaintext symbol yields step 0, which is exactly the "s = 0 only for one rare symbol" behaviour your model needs, provided the skipped symbol is rare (EA, or the rarest rune) and the cipher is chained on ciphertext.
- **(b) A non-repeating flat keystream.** Cicada's documented flat sources:
  - whole-file XOR pads: mp3, the 560.xx datasets;
  - prime/totient streams;
  - per-solver offsets.
  
  The datasets fail as direct keystreams (finding 0.7). Never-tested flat sources include:
  - the **unused P.S. number** (131 digits; about 89 base-29 digits; repeats with period 89 or 131);
  - pads keyed by the **1031/1229/1259 Parable factors** as offsets;
  - the **cicada PNG / base64 text** (a natural "next layer" artifact).
- **(c) DJU BEI.**
  - No historical text matches.
  - [SPEC] Cicada's habit of ending sections with the Parable/instar refrain suggests the last two words of seg 15 restate a phrase from early seg 13. Under ciphertext autokey, identical 6-rune ciphertext needs identical plaintext and identical key differences. If plain and key positions differ, the coincidence is a chance event with probability on the order of 29^-5 per alignment. So DJU BEI more likely marks a key reset or **key reuse at a fixed offset between those two points**: page 42 line 1 versus page 70 end.
  - That offset is computable. Treat (position at p70) − (position at p42) as a candidate key period or pad offset, and test it as a period specifically.
- **(d) "Words are the map, meaning the road, numbers the direction."**
  - In Cicada's history, "numbers" of words always means GP sums or prime values (gematrified access codes, the page-1 warning about "the words or their numbers").
  - "Direction" suggests **sign or order** (atbash or reversal, add versus subtract) or a pointer.
  - [SPEC] The keystream might be the GP sums of the LP's own words (solved or unsolved), used as a running key with the direction (±) taken from parity or primality.
- **(e) "Key all around you" / "shed our circumferences".**
  - "Key all around you" is resolved as the 2013 Twitter/mp3 pointer (finding 0.3). Treat it as a methodological hint (the key is in the surrounding artifacts), not as the LP's page border.
  - "Shed circumferences" first appeared on the 2013 mp3, which was a **pad**. [SPEC] It may mean removing outer layers, i.e. undoing an outer chained layer first, which is consistent with your autokey model.

---

## 4. Ranked, testable hypotheses (consistent with the constraints)

Notation:
- `C` = unsolved runes (segments 7–15);
- `s[i] = C[i] − C[i−1] mod 29`;
- the harness = `full_model_harness.scan(K, offsets, restarts)`;
- also score with `structure_score.py`.

1. **The skip rule *is* the doublet mechanism (Vigenère-with-skip chained on ciphertext).**
   - Procedure: `c[i] = c[i−1] + x[i] + k[j]` with the LP's own convention. If the plaintext is the skip symbol, write `c[i] = c[i−1]` and do not advance `j`.
   - Why: it reuses the solved sections' exact "F not encrypted, key frozen" rule. The skipped symbol would now be the rare one (EA, or a rotation mapping EA to F).
   - Test: in the harness, use `skip=True` with keys from Cicada's own vocabulary: DIVINITY, FIRFUMFERENFE, CIRCUMFERENCE, INSTAR, EMERGE, PARABLE, PILGRIM, PRIMALITY, KOAN, 3301 and 1033 in base 29 ("3QO" ↔ [3,26,24]), and the keys of solved sections run backwards.
   - Periodic keys up to 40 are excluded, so this only applies to keys longer than 40 runes or to non-periodic phrases. Use the full solved plaintext as the key (book-like but LP-internal), with the mod-28 inner shift.
2. **A running key from LP word GP sums ("numbers are the direction").**
   - Key stream = GP sum (sum of primes) of each plaintext word of the solved LP pages, or of the unsolved ciphertext words. Apply it per rune, or per word with the same value for all runes of a word. Take it mod 28 or 29, with sign flipped where the sum is prime (or by word parity).
   - Test: harness with key advancing per rune and per word. The harness needs a per-word index; add a `WORDIDX` from lp.json.
3. **Pad continuation.** The 2013 pad use of `560.13` ended at the GP-JPG region (64,167) or at the onion offsets.
   - Key = `560.13[64167:]` or `_560.00`. Convert with base-29 **digit expansion of large chunks**, the BASE29 command's style, rather than byte mod 29. For example, read the pad as one big integer and emit base-29 digits.
   - Byte mod 29 is excluded here; big-integer base 29 is not.
   - Test: `int.from_bytes(pad[o:o+N], 'big')` → base-29 digits, for o in {0, 64167, 20709, 12821} → harness.
4. **The Valēte P.S. number as a key.** It is the only 2012 artifact never used.
   - Try its 131 decimal digits, its base-29 digits (about 89), and the base-29 expansion of P.S. × 3301 or P.S. mod other numbers.
   - Use as a repeating key with period 89 or 131, which is above your tested maximum of 40. Also try it as an AES/ChaCha seed (SHA-256 of the decimal string).
   - Test: harness, offsets 0..period−1, skip on/off. Also run the periodic-column IoC test at periods 41–200 with the autokey removed.
5. **Parable factors as prime-stream anchors.**
   - The prime/totient stream starts at the 1031st prime, at prime 1031, or at the π-index of 1229 or 1259. Also try "start at 1033 / 3301 (the prime_echo pause points)".
   - Also try the reversed stream (3301 → 2, as "1033" mirrors "3301").
   - Test: harness with K = φ(p_n) for n starting at 174 (1033), 464 (3301), 1031, 1229, 1259, forward and reversed. Probably already partly covered by retest_totient-prime_offsets: check that its scan covered reversed streams and the inner mod-28 layer.
6. **Modular exponentiation chain (DH/RSA heritage).**
   - Ciphertext rune = g^(x + previous) mod 29, i.e. index arithmetic in the multiplicative group (primitive root 2 or 3 mod 29). This is an autokey in the exponent: multiplication maps to addition of discrete logs.
   - The exponent ciphers already tested used a constant or stream exponent, not an **autokey in log space** with 0 as the fixed point.
   - Test: map runes 1..28 to discrete logs base 2 mod 29, apply the difference autokey in log space (mod 28), keep 0 as its own symbol, then compute IoC.
7. **The 2014 transposition ("For those who have fallen behind") style as an outer layer.** Finish decoding p08 to learn the transposition family Cicada uses. Then test the same family as a pre-autokey step on page blocks. The 2D/grid tests argue against this, so rank it low.
8. **DJU BEI as a key-reuse marker.**
   - Compute d = index(p70 copy) − index(p42 copy) in the unsolved stream.
   - Test the periodic-column IoC at period d and at its divisors, on the autokey-removed stream and the mod-28 inner stream.
   - Test a depth search at shift d (already covered by depth_search at all offsets, so this is a confirmation only).
9. **The cicada PNG (finding 0.1) as a pad.** Its pixel grey levels 0–7 form a 3-bit stream of 272,483 pixels. Also try the base64 text itself (base64 index 0–63, mod 28/29).
   - Cicada hid this image inside a pad, and it was never used publicly, so it is a candidate "flat" key.
   - Test: harness with K = PNG pixels (row-major and column-major), K = base64 indices, and K = pixel triples combined to base 8 → mod 29.
10. **Interconnectedness.mp3 / 761.mp3 / 4gq25.jpg bytes as XOR pads (byte → rune via mod or base-29 expansion).**
    - Cicada's only fully documented pad was an mp3, and "Skip" was a declared parameter.
    - Test: harness on mp3 bytes (raw, mod 29, mod 28) with skip values 1–8 (every k-th byte). Skip ≠ 0 has never been tried.

The scripts below support the ranking: I already ran the dataset keystreams through the harness, and they fail (§0.7).

---

## 5. Caveats

- The docs in `ON` stop at the 2014 LP. The 2015 pastebin and the 2016/2017 messages are not stored locally, so their text is unverified (no OutGuess binary was available, and building one was refused).
- Finding 0.1 may already be known in the community. It is not in the local docs or the analysis README.
- Scratchpad outputs (under /tmp/claude-0/-home-user-iddqd/c4d0f226-87a8-5085-be90-4aec3e9a339e/scratchpad/):
  - `found/560_13_xor_gematria.png`
  - `found/560_13_xor_gematria.bin`
  - `found/planes.png`
  - `found/lp03.jpg`
  - `ds_test.py`
  - `tw_xor.jpg`
