"""Other 'coigns of vantage' on the unsolved text, and calculus-style transforms, each scored with the
structure_score battery (unigram, bigram, periodic IoC 2-40, lag repeats, doublets, 5-gram repeats, compressibility)
and compared with the same view of 40 null texts. Null = random runes in the SAME layout (pages, lines, words),
drawn with the observed rune frequencies and the observed reading-order doublet rate. p = share of nulls whose
combined (max-z) score is >= the real one.
Views: reading order; pages rotated (read down columns, by rune index in the line); rotated the other way; page
stack (the same line/column cell read through all pages: the 3D matrix's depth axis); acrostic streams (word,
line, clause first/last runes). Calculus: finite differences of order 1-3 (order 1 = ciphertext autokey removal),
running sums of order 1-2 (integration), formal derivative / integral of a polynomial over GF(29) (c_i * i and
c_i / i, with i the position in page, line or word), and differences taken down columns."""
import os, sys, collections, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lp_common import UNS
from structure_score import battery, KEYS
C = np.array([r['c'] for r in UNS]); N = len(C)
seg = np.array([r['seg'] for r in UNS]); page = np.array([r['page'] for r in UNS]); line = np.array([r['line'] for r in UNS])
col = np.array([r['col'] for r in UNS]); word = np.array([r['word'] for r in UNS]); clause = np.array([r['clause'] for r in UNS])
freq = np.bincount(C, minlength=29) / N; drate = np.mean(C[1:] == C[:-1])
rng = np.random.default_rng(29)
def null_text():
    x = np.empty(N, int); x[0] = rng.choice(29, p=freq)
    draws = rng.choice(29, size=3 * N, p=freq); k = 0
    for i in range(1, N):
        if rng.random() < drate: x[i] = x[i - 1]; continue
        while draws[k] == x[i - 1]: k += 1
        x[i] = draws[k]; k += 1
    return x
def order_cols(rev=False):
    key = np.lexsort((line if not rev else -line, col if not rev else -col, page)); return key
O_COL, O_COLR = order_cols(), order_cols(True)
O_DEPTH = np.lexsort((page, col, line))
def firsts(g): return np.r_[True, g[1:] != g[:-1]]
def lasts(g): return np.r_[g[1:] != g[:-1], True]
def pos_in(g):
    out = np.zeros(N, int)
    for i in range(1, N): out[i] = out[i - 1] + 1 if g[i] == g[i - 1] else 0
    return out + 1
PI = {'page': pos_in(page), 'line': pos_in(page * 100 + line), 'word': pos_in(word)}
INV = np.array([0] + [pow(i, -1, 29) for i in range(1, 29)])
def diff(x, k, g=seg):
    for _ in range(k):
        y = (x[1:] - x[:-1]) % 29; keep = g[1:] == g[:-1]; x, g = y[keep], g[1:][keep]
    return x
def integ(x, k, g=seg):
    for _ in range(k):
        y = np.zeros_like(x); acc = 0
        for i in range(len(x)):
            acc = x[i] if i == 0 or g[i] != g[i - 1] else (acc + x[i]) % 29; y[i] = acc
        x = y
    return x
def formal(x, which, inverse):
    i = PI[which] % 29; ok = i != 0
    return (x[ok] * (INV[i[ok]] if inverse else i[ok])) % 29
VIEWS = {
    'reading order': lambda x: x,
    'rotated: read down columns': lambda x: x[O_COL],
    'rotated other way (up, right-to-left)': lambda x: x[O_COLR],
    '3D depth: same cell through pages': lambda x: x[O_DEPTH],
    'acrostic: word first runes': lambda x: x[firsts(word)],
    'telestich: word last runes': lambda x: x[lasts(word)],
    'line first runes': lambda x: x[firsts(page * 100 + line)],
    'line last runes': lambda x: x[lasts(page * 100 + line)],
    'clause first runes': lambda x: x[firsts(clause)],
    'd/dx order 1 (= autokey removal)': lambda x: diff(x, 1),
    'd/dx order 2': lambda x: diff(x, 2),
    'd/dx order 3': lambda x: diff(x, 3),
    'integral order 1 (running sum)': lambda x: integ(x, 1),
    'integral order 2': lambda x: integ(x, 2),
    'd/dx down columns': lambda x: diff(x[O_COL], 1, (page * 1000 + col)[O_COL]),
    'integral down columns': lambda x: integ(x[O_COL], 1, (page * 1000 + col)[O_COL]),
    'formal derivative c*i, i in page': lambda x: formal(x, 'page', False),
    'formal integral c/i, i in page': lambda x: formal(x, 'page', True),
    'formal derivative c*i, i in line': lambda x: formal(x, 'line', False),
    'formal integral c/i, i in line': lambda x: formal(x, 'line', True),
    'formal derivative c*i, i in word': lambda x: formal(x, 'word', False),
    'formal integral c/i, i in word': lambda x: formal(x, 'word', True),
    'formal integral of d/dx (c_i-c_i-1)/i, page': lambda x: formal(np.r_[x[0], (x[1:] - x[:-1]) % 29], 'page', True),
}
nulls = [null_text() for _ in range(40)]
print(f'{"view":46s} {"n":>6s} {"combined z":>10s} {"top metric":>16s} {"p":>6s}')
for name, f in VIEWS.items():
    real = battery(f(C), 29); nb = [battery(f(x), 29) for x in nulls]
    st = {k: (np.mean([b[k] for b in nb]), np.std([b[k] for b in nb]) or 1) for k in KEYS}
    def comb(b):
        z = {k: ((st[k][0] - b[k]) if k == 'compressibility' else (b[k] - st[k][0])) / st[k][1] for k in KEYS}
        z['doublets'] = abs(z['doublets']); return max(z.values()), max(z, key=z.get)
    rz, rk = comb(real); nz = [comb(b)[0] for b in nb]
    print(f'{name:46s} {len(f(C)):6d} {rz:10.2f} {rk:>16s} {np.mean(np.array(nz) >= rz):6.2f}', flush=True)
