"""Pooled column IoC for every period 1..2000 (raw, autokey-removed diff, and in-word-only diff),
with the z of the pooled same-rune pair count against the flat expectation."""
import numpy as np
from load import ct
C=ct(); c=np.array([r for cl in C for w in cl for r in w]); N=len(c)
def scan(x,name):
    n=len(x); out=[]
    for P in range(1,2001):
        eq=0;pairs=0
        for L in range(P,n,P):  # pairs at distance multiples of P -> equality count
            eq+=(x[L:]==x[:-L]).sum(); pairs+=n-L
        exp=pairs/29; z=(eq-exp)/np.sqrt(exp*(28/29))
        out.append((z,P,eq/pairs*29))
    out.sort(reverse=True)
    print(name,[(P,round(z,1),round(v,3)) for z,P,v in out[:8]])
scan(c,'raw')
scan((c[1:]-c[:-1])%29,'diff')
scan((c[1:]+c[:-1])%29,'sum')
