"""DJU BEI cribs under multiplicative (c = p*k mod 29) and exponential (c = p^k mod 29) ciphers,
plus GP sums of the cribs versus the ciphertext words."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'crib_djubei.py')).read()
exec(src.split('# positions of every unsolved rune')[0])        # GP, LAT, PR, runes(), W3
ct = [IDX[c] for c in 'ᛞᛄᚢᛒᛖᛁ']
gsum = lambda r: sum(PR[x] for x in r)
print('ciphertext: DJU = %d, BEI = %d, total %d' % (gsum(ct[:3]), gsum(ct[3:]), gsum(ct)))
def mul_key(c, p):
    if p == 0: return '·' if c == 0 else '∅'          # 0*k = 0 only
    return (c * pow(p, -1, 29)) % 29
def exp_keys(c, p):
    ks = [k for k in range(28) if pow(p, k, 29) == c % 29 and not (p == 0 and k == 0)]
    return ks
cribs = ['OUR OWN', 'AND YOU', 'SEE YOU', 'YOU ARE', 'FOR YOU', 'FOR ALL', 'ALL ARE', 'AND ALL', 'NOT ONE', 'HIS OWN',
         'WAS NOT', 'ARE NOT', 'YOU MAY', 'ONE DAY', 'ALL OUR', 'OUR WAY', 'YOU CAN', 'WHO ARE', 'ARE ONE', 'GOD WAS']
print('\ncrib       GP sums      additive key        multiplier k (c=p*k)       exponent k (c=p^k), all solutions mod 28')
for c in cribs:
    a, b = c.split(); r = runes(a) + runes(b)
    if len(runes(a)) != 3 or len(runes(b)) != 3: continue
    add = [(ct[i] - r[i]) % 29 for i in range(6)]
    mul = [mul_key(ct[i], r[i]) for i in range(6)]
    ex = [exp_keys(ct[i], r[i]) for i in range(6)]
    exs = ['/'.join(map(str, e)) if e else '∅' for e in ex]
    print(f'{c:9s} {gsum(r[:3]):3d}+{gsum(r[3:]):3d}={gsum(r):3d}  {str(add):24s} {str(mul):30s} {exs}')
# whole-vocabulary search: a constant key across all six runes (= monoalphabetic), or constant per word
print('\nsearch over all %d x %d word pairs:' % (len(W3), len(W3)))
items = list(W3.items())
for name in ('multiplicative', 'exponential'):
    const6, const_per_word = [], []
    for ra, wa in items:
        for rb, wb in items:
            r = ra + rb
            if name == 'multiplicative':
                ks = [{mul_key(ct[i], r[i])} if isinstance(mul_key(ct[i], r[i]), int) else set() for i in range(6)]
            else:
                ks = [set(exp_keys(ct[i], r[i])) for i in range(6)]
            all6 = set.intersection(*ks) if all(ks) else set()
            w1 = set.intersection(*ks[:3]) if all(ks[:3]) else set(); w2 = set.intersection(*ks[3:]) if all(ks[3:]) else set()
            if all6: const6.append((wa + ' ' + wb, sorted(all6)))
            elif w1 and w2: const_per_word.append((wa + ' ' + wb, sorted(w1), sorted(w2)))
    print(f'  {name}: one key for all 6 runes -> {len(const6)} pairs {const6[:10]}')
    print(f'  {name}: one key per word        -> {len(const_per_word)} pairs, e.g. {const_per_word[:8]}')
# GP-sum relations
print('\nvocabulary 3-rune words with the same GP sum as the ciphertext words: DJU(129):',
      [w for r, w in W3.items() if gsum(r) == 129], ' BEI(159):', [w for r, w in W3.items() if gsum(r) == 159])
print('3+3 pairs whose total GP sum is 288:', [(W3[a] + ' ' + W3[b]) for a in W3 for b in W3 if gsum(a) + gsum(b) == 288][:25])
tot = sum(1 for a in W3 for b in W3 if gsum(a) + gsum(b) == 288)
print('\npairs with total 288: %d of %d (%.2f%%); plausible-crib list: %d of %d hit 288' % (
    tot, len(W3) ** 2, 100 * tot / len(W3) ** 2,
    sum(1 for c in cribs if len(runes(c.split()[0])) == 3 and len(runes(c.split()[1])) == 3 and gsum(runes(c.split()[0]) + runes(c.split()[1])) == 288),
    sum(1 for c in cribs if len(runes(c.split()[0])) == 3 and len(runes(c.split()[1])) == 3)))
