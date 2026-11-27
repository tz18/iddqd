# Round 1: Mr Annoying's report

## Verdict: acceptable with complaints

The cipher itself is Cicada-grade. It has three steps, a public key (the primes) and no choices the encryptor makes
per word or per clause. Anyone who removes the autokey and tries "divide by the primes" decrypts it. I checked:
`decrypt.py` gives an exact match (2,448 runes, 0 differences), and the same thing done blind (difference, then
multiply by p_i^27, with 29 skipped) gives THESHEDDINGTHEINSTARDOESNOTMOURN... at once. What I object to is the
spelling layer and the write-up. The spelling breaks the one habit every solved page shares, and it was picked to hit
a statistic. DESIGN.md also claims more than the self-check supports in four places, and it presents the solved-page
precedents as closer to this design than they are.

## Degrees of freedom

DESIGN.md says there are 4 structural choices and 3 numeric parameters. I count 8 structural choices, 3 numeric
parameters and 1 hidden lever.

| # | Choice | Kind | Decryptor must guess? | Natural or tuned |
|---|---|---|---|---|
| 1 | Letter-by-letter spelling (no ᚦ ᛝ ᛠ ᛇ ᛟ ᚫ ᛡ) | structural | no (the output stays readable either way) | **tuned to target 5**, as DESIGN.md says ("the only lever on word lengths") |
| 2 | Inner operation is multiplication, not shift | structural | yes (add / sub / mul / div) | partly tuned: it is what makes F, and only F, go to 0 |
| 3 | Key stream is the primes, not totient(p) | structural | yes (2 or 3 options) | natural |
| 4 | 29 passed over in the prime list | structural | yes (skip / keep / stop) | forced, but unstated in the hint |
| 5 | Key index advances on F as well | structural | yes (advance / skip) | **contradicts** the solved pages (see C3) |
| 6 | Ciphertext autokey, not plaintext autokey or none | structural | yes (sign and type, about 4 options) | natural, but has no LP precedent |
| 7 | One chain over the whole text, no restarts | structural | yes (text / page / clause / word restarts) | natural |
| 8 | Plaintext word and clause breaks shown | structural | no | natural |
| 9 | zero_rune = F | numeric | fixed by the hint | natural |
| 10 | iv = 0 | numeric | barely (it affects only rune 0) | natural |
| 11 | prime_offset = 0 | numeric | yes, but 0 is the obvious first try | natural |
| 12 | The plaintext's F rate (1.27%) | hidden lever | no | **sets target 1 directly** (see C2) |

Search cost: with the hint, choices 2-7 give about 4 x 2 x 2 x 2 x 4 x 3 = 384 configurations (about 2^9), and each
one is checked by reading the output. Without the hint, the 2^20 in DESIGN.md is fair. The secret key is about 0
bits. On key size the design passes easily.

## Complaints, ranked by severity

**C1 (severe): letter-by-letter spelling breaks Cicada's most consistent habit, and it was chosen to hit a number.**
Every solved LP page writes TH, NG/ING, EA, EO, OE, AE and IA/IO with their own runes. THE is ᚦᛖ, never ᛏᚻᛖ. Gematria
Primus exists to give these digraphs single runes, so a Cicada who spells T-H throws away its own alphabet. DESIGN.md
openly says it chose this to move the 2-rune share from about .24 to .16. That is a choice tuned to a target, not one
that follows from the cipher. It also does not fully land: the word-length chi2 against the target is 34.4 on 9 df
(p about 1e-4), and the mean is 4.07 +/- 0.08 against 4.47, which is 5 SE off. "Roughly" overstates the match.
Letter spelling may well be what the unsolved pages show (README line 142, line 248). Even so, a design that uses it
must give Cicada a reason, or must flag it as the design's biggest assumption. Right now it is framed as a free
lever.

**C2 (severe): the doublet "partial match" is a property of this plaintext, not of the cipher.** The doublet rate
equals the plaintext F rate exactly. This plaintext has F at 1.27%. Blake's *Marriage of Heaven and Hell* spelled
letter by letter (`sources/`) has F at 2.42%, which would give a doublet rate of about 2.4%: 3.7 times the target and
70% of the random level. Cicada wrote this plaintext, so this is a twelfth parameter that no one stated. Applied to
ordinary English, the design reproduces target 1 badly, not "partly". DESIGN.md should say that the doublet rate is
f_F(plaintext), and should give the expected value for a reference corpus.

**C3 (moderate): the solved-page precedents are misstated.**
- "F is not encrypted" on the solved pages means a plaintext F appears as ᚠ in the ciphertext and the key does not
  advance there. In this design, F does not appear as F. It appears as a repeat of the previous ciphertext rune, and
  the key does advance. These are three differences (visibility, form, key advance) that share one slogan. A solver
  who takes the hint literally looks for literal ᚠ and a key that pauses, and finds neither.
- "The totient page's key was the primes" is wrong. The solved stream was phi(p) = p - 1, used as a shift. Primes
  used as a multiplier mod 29 have no LP precedent.
- Ciphertext autokey has no precedent on the solved pages either. The design stacks two operations Cicada never
  showed (multiplication mod 29, autokey) on top of a third that breaks a habit (C1). The solved ciphers are each a
  single substitution or shift layer.

**C4 (moderate): the table claims more than the self-check shows.**
- Target 9, "yes": the round has 7.4 words and 30 runes per clause, against 17.2 and 77 on the unsolved pages, and
  0 one-word clauses against 2. Clause lengths come from the plaintext's line breaks and do not match. At best this
  is "not tested". Calling it "yes" is wrong.
- Target 5, "roughly": see C1 (p about 1e-4).
- Target 3, mechanism: the flatness comes from the ciphertext autokey alone. Any stream, periodic or not, would
  flatten the frequencies under autokey. The "aperiodic multiplier" is not why chi2 is 32.5.
- Target 11, "yes": the d stream (d != 0) has rune 1 at z +2.8, above the expected maximum of about +2. That is
  mild, but it is not "no rune over-represented".

**C5 (moderate): this cipher family is already refuted on the real pages, so a statistical match says little.**
DESIGN.md admits this, which counts in its favour. But a model in which one plaintext letter goes to 0 implies an
English letter at 0.66% (C2 and the design's own target-2 section). The doublet positions (48/32/19 first/middle/
last, chi2 9.7, and 2.5% across gaps against 0.79%) are a strong fingerprint against the whole family. As a
rehearsal, the round shows that this family fails targets 1, 2, 6, 7 and 8. It does not show a cipher that could
explain the unsolved pages.

**C6 (minor): the hint does not fix every parameter, contrary to DESIGN.md.** "THE PRIMES ARE SACRED. EACH RUNE
CARRIES WHAT CAME BEFORE. F IS NOT ENCRYPTED" does not say multiply rather than add or subtract. Its natural reading
of "F is not encrypted" gives the wrong key-advance rule (C3). It says nothing about 29 or restarts. The solver can
still brute-force these (about 2^9), so the round remains solvable. But "fixes every parameter" is false.

**C7 (minor): F as the zero rune works only because F is index 0.** "Multiplication leaves 0 alone" is a fact about
residues. It is not a rule Cicada stated. If zero_rune were anything other than F, the step would need a rotation
first, which is an extra layer (as in `full_model_harness.py`). Choosing F is neat, but it is a coincidence of the
indexing, not a derived mechanism.

## What the Cicada must change to satisfy me

1. **Spelling:** either use LP digraph spelling, or keep letter spelling and give it an explicit stated reason and
   a hint ("the runes are letters" or similar). List it in the parameter table as the design's largest assumption
   and as tuned to target 5. Report the word-length chi2, not "roughly".
2. **Doublet claim:** state that the doublet rate equals f_F(plaintext). Give the expected rate on a reference corpus
   (the Blake text gives about 2.4%), and list the plaintext's F rate as a parameter. Do not count target 1 as
   "partly" met unless it holds for generic English.
3. **Precedents:** rewrite the hint section. Solved-page F skipping keeps a visible ᚠ and pauses the key. The
   totient page used phi(p) as a shift. Multiplication and autokey are new. Either make F behave as it does on the
   solved pages (visible ᚠ, key paused), or say plainly that this is a different rule that shares the name.
4. **Table:** change target 9 to "no / not tested" with the real clause statistics. Credit target 3 to the autokey.
   Soften target 11.
5. **Hint:** write one that states the operation (multiply or divide by the primes) and the key-advance rule, or
   drop the claim that it fixes every parameter.
6. **Parameter count:** use the 8 + 3 + 1 table above, or argue why any of its rows should not count.
