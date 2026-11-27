"""Apply the round-1 attack to the unsolved pages: d = c[i]-c[i-1], p = d / q[j], q = primes without 29 (and with 29,
and totients), j = rune index from the start of each section or page + offset 0..3000. Report best IoC per unit,
against the best-of-offsets for shuffled runes of the same unit."""
import sys, numpy as np, collections
sys.path.insert(0,'/home/user/iddqd/liber-primus__analysis')
from lp_common import UNS
rng=np.random.default_rng(3)
def primes(N):
    s=np.ones(N+1,bool); s[:2]=0
    for i in range(2,int(N**.5)+1):
        if s[i]: s[i*i::i]=0
    return np.nonzero(s)[0]
P=primes(400000)
streams={'primes-no-29':P[P!=29]%29,'totient':(P-1)%29}
inv=np.array([0]+[pow(x,27,29) for x in range(1,29)])
def best(c,s,offs=3000):
    d=(np.diff(np.concatenate([[0],c])))%29; n=len(d)
    K=s[np.arange(offs)[:,None]+np.arange(n)[None,:]]
    X=(d[None,:]*inv[K])%29; X=np.where(K==0,-1,X)
    out=np.zeros(offs); m=(X>=0).sum(1)
    for v in range(29):
        cnt=(X==v).sum(1); out+=cnt*(cnt-1)
    v=out/(m*(m-1))*29; return v.max(), int(v.argmax())
for unit in ('seg','page'):
    g=collections.OrderedDict()
    for r in UNS: g.setdefault(r[unit],[]).append(r['c'])
    for sn,s in streams.items():
        rows=[]
        for k,c in g.items():
            if len(c)<200: continue
            c=np.array(c[:1500]); v,o=best(c,s); ctrl=best(rng.permutation(c),s)[0]
            rows.append((k,len(c),round(v,3),o,round(ctrl,3)))
        print(unit,sn,'max over units',max(r[2] for r in rows),'| control max',max(r[4] for r in rows))
