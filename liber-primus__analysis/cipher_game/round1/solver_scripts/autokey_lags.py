"""Ciphertext autokey at any lag: IoC of c[i] -/+ c[i-L] for L=1..1000, and of a*c[i]+b*c[i-L] (all a,b) for L<=60."""
import numpy as np
from load import ct
C=ct(); c=np.array([r for cl in C for w in cl for r in w]); N=len(c)
def ioc(x):
    cnt=np.bincount(x,minlength=29); n=len(x); return (cnt*(cnt-1)).sum()/(n*(n-1))*29
r=[]
for L in range(1,1000):
    for nm,x in (('-',(c[L:]-c[:-L])%29),('+',(c[L:]+c[:-L])%29)):
        v=ioc(x); r.append(((v-1)/np.sqrt(2*28/len(x)**2*1.0)/1,v,L,nm))
r.sort(reverse=True); print([(L,nm,round(v,3),round(z,1)) for z,v,L,nm in r[:8]])
best=[]
for L in range(1,61):
    for a in range(1,29):
        for b in range(1,29):
            best.append((ioc((a*c[L:]+b*c[:-L])%29),L,a,b))
best.sort(reverse=True); print(best[:5])
