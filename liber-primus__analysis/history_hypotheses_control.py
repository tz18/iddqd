"""Best-of-83 control for history_hypotheses.py: replace every key by a random key of the same length/range and
take the best structure score over all 83 keys; repeat."""
import os, sys
import numpy as np
sys.argv = ['x']
exec(open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0] if os.path.isabs(sys.argv[0]) else 'history_hypotheses.py')), 'history_hypotheses.py')).read().split("rng = np.random.default_rng(42)")[0])
rng = np.random.default_rng(2024)
maxes = []
for rep in range(5):
    best = max(evaluate(rng.integers(np.asarray(K).min(), np.asarray(K).max() + 1, len(K)))[1] for K in keys.values())
    maxes.append(best); print('replicate', rep, 'best struct over 83 random keys: %.2f' % best, flush=True)
print('real best over 83 keys: 6.97;  control bests:', [round(m, 2) for m in maxes])
