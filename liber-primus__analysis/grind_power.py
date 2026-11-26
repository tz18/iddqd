"""Power of grind_period5.py: encrypt known English with random per-word period-5 shift keys and grind with a
dictionary that does NOT contain that text. (a) plaintext = solved LP (different author), dictionary = Blake only;
(b) plaintext = Jerusalem (Blake), dictionary = Blake minus Jerusalem. Reports, for words of 7+ runes: share whose true
plaintext is in the dictionary (coverage), words with >= 1 match for the real encryption vs the same words shuffled."""
import os, sys, re, glob, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
from lp_common import R, d
src = open(os.path.join(HERE, 'sum_preserving.py')).read(); exec(src[src.index('L2I = {'):src.index('bl = re.findall')])
rng = np.random.default_rng(4)
B = os.path.join(HERE, 'sources', 'blake')
def build(texts):
    D = collections.defaultdict(set)
    for t in texts:
        for w in set(x.upper() for x in re.findall(r"[A-Za-z]+", t)):
            for dig in (True, False):
                s = tuple(spell(w, dig))
                if len(s) >= 7: D[len(s)].add(s)
    return {L: np.array(sorted(v)) for L, v in D.items()}
def has_match(DA, c):
    if len(c) not in DA: return False
    P = DA[len(c)]; return bool(((P[:, 5:] - P[:, :-5]) % 29 == (c[5:] - c[:-5]) % 29).all(1).any())
def run(label, plain_words, DA):
    pw = [np.array(w) for w in plain_words if len(w) >= 7]
    cov = np.mean([len(w) in DA and (DA[len(w)] == w).all(1).any() for w in pw])
    enc = [(w + np.resize(rng.integers(0, 29, 5), len(w))) % 29 for w in pw]
    real = sum(has_match(DA, c) for c in enc)
    allr = np.concatenate(enc); fk = []
    for _ in range(20):
        x = rng.permutation(allr); i = 0; f = 0
        for w in enc: f += has_match(DA, x[i:i + len(w)]); i += len(w)
        fk.append(f)
    print(f'{label}: {len(pw)} words of 7+ runes, dictionary coverage {cov:.2f}; words with a match: encrypted {real} vs shuffled {np.mean(fk):.1f} +/- {np.std(fk):.1f}  -> excess {real - np.mean(fk):.0f} ({(real - np.mean(fk)) / len(pw):.2f} per word)')
# (a) solved LP plaintext, LP spelling as in the book; dictionary = all Blake
lp_words = collections.OrderedDict()
for r in R:
    if d['segments'][r['seg']]['solved']: lp_words.setdefault(r['word'], []).append(r['p'])
run('(a) solved LP plaintext, Blake dictionary', list(lp_words.values()), build([open(os.path.join(B, '_ALL.txt')).read()]))
# (b) Jerusalem with letter-by-letter spelling; dictionary = Blake without Jerusalem
jer = ' '.join(open(f).read() for f in glob.glob(os.path.join(B, 'Jerusalem*')))
rest = [open(f).read() for f in glob.glob(os.path.join(B, '*.txt')) if 'Jerusalem' not in f and not f.endswith('_ALL.txt')]
jw = [spell(w.upper(), False) for w in re.findall(r"[A-Za-z]+", jer)][:6000]
run('(b) Jerusalem (letter by letter), Blake-minus-Jerusalem dictionary', jw, build(rest))
print('\nunsolved result for comparison: 209 real vs 206 +/- 6 fakes over 559 words (excess 3, 0.01 per word)')
