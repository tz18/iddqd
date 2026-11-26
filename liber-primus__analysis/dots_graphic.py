"""The 5-dot graphic: find large round filled dots in every page scan, then compare the point sets.
Finds the same five dots on pages 24 (unsolved), 40 (unsolved, flipped top-bottom) and 73 (Parable, flipped left-right)."""
import os, glob
import numpy as np
from PIL import Image
from scipy import ndimage
HERE = os.path.dirname(os.path.abspath(__file__))
for f in sorted(glob.glob(os.path.join(HERE, '..', 'liber-primus__images--full', '*.jpg'))):
    im = np.asarray(Image.open(f).convert('L')); H, W = im.shape
    m = im < 110; lab, n = ndimage.label(m); objs = ndimage.find_objects(lab); s = ndimage.sum(m, lab, range(1, n + 1))
    dots = []
    for sl, a in zip(objs, s):
        h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
        if 1500 < a < 20000 and 0.8 < h / w < 1.25 and 0.7 < a / (h * w) < 0.86:
            cy, cx = ndimage.center_of_mass(m[sl]); dots.append((round(sl[1].start + cx), round(sl[0].start + cy)))
    if len(dots) >= 3:
        xy = np.array(sorted(dots, key=lambda t: (t[1], t[0])), float); c = xy - xy.mean(0)
        D = sorted(np.hypot(*(xy[i] - xy[j])) for i in range(len(xy)) for j in range(i + 1, len(xy)))
        print(f'{os.path.basename(f)} ({W}x{H}): {len(dots)} dots at {[tuple(map(int, p)) for p in xy]}')
        print(f'   centred {[tuple(np.round(v).astype(int)) for v in c]}; pairwise distances {[round(v) for v in D]}')
