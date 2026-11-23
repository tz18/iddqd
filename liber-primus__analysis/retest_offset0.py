"""Principled subset: keys start at their beginning (offset 0); stream runs continuously or restarts at each
segment / page; both signs; raw, autokey-removed and mod-28 non-zero targets. Same structure score.
Control: identical settings with random keys (best over the same number of settings)."""
import os, sys
import numpy as np
__file__ = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'retest_all.py')
exec(open(__file__).read().split("if __name__ == '__main__':")[0])
NZPOS = {k: v[1:][D != 0] for k, v in POS.items()}
def settings(streams):
    for sname, K in streams.items():
        for sch in ('whole', 'segment', 'page'):
            for tname, T, pos, m in (('raw', C, POS[sch], 29), ('autokey removed', D, POSD[sch], 29), ('mod-28 non-zero', NZ, NZPOS[sch], 28)):
                k = K[pos % len(K)] % m
                for op in (1, -1):
                    yield f'{sname}|{sch}|{tname}|{"-" if op > 0 else "+"}', (T - op * k) % m, m
def run(streams):
    out = [(score(x, m)[0], lab) for lab, x, m in settings(streams)]
    return max(out), len(out), out
real_streams = {**{'wisdom ' + k: v for k, v in wisdom_streams(W).items()}, 'totient': (PRIMES - 1), 'primes': PRIMES}
(best, lab), n, allres = run(real_streams)
rng = np.random.default_rng(7)
ctrl = []
for r in range(20):
    rs = {k: rng.integers(0, 10 ** 6, len(v)) for k, v in real_streams.items()}
    ctrl.append(run(rs)[0][0])
ctrl = np.array(ctrl)
print(f'{n} principled settings. best real score {best:.2f} at {lab}')
print(f'control (random keys, same {n} settings), best per run: median {np.median(ctrl):.2f}, max {ctrl.max():.2f}; P(control >= real) = {np.mean(ctrl >= best):.2f}')
print('top 5 real:', [(round(s, 2), l) for s, l in sorted(allres, reverse=True)[:5]])
print('reference (no peel): raw 27.9, autokey removed 40.7, mod-28 non-zero 2.0')
