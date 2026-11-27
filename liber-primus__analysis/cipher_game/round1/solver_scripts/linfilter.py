"""Search p[i] = a0*c[i] + a1*c[i-1] + a2*c[i-2] (mod 29), stream continuous or restarted per word / per clause.
Score: IoC of output (English in LP spelling ~1.7-1.8)."""
import numpy as np, itertools
from load import ct
C=ct()
def build(mode):
    seq=[];prev1=[];prev2=[]
    flat=[r for c in C for w in c for r in w]
    i=0
    for c in C:
        cstart=i
        for w in c:
            wstart=i
            for k,r in enumerate(w):
                lo={'cont':0,'word':wstart,'clause':cstart}[mode]
                p1=flat[i-1] if i-1>=lo else -1
                p2=flat[i-2] if i-2>=lo else -1
                seq.append(r);prev1.append(p1);prev2.append(p2); i+=1
    return np.array(seq),np.array(prev1),np.array(prev2)
def ioc(x):
    c=np.bincount(x,minlength=29); n=len(x); return (c*(c-1)).sum()/(n*(n-1))*29
for mode in ('cont','word','clause'):
    s,p1,p2=build(mode); m=(p1>=0)&(p2>=0)
    res=[]
    for a0 in range(1,29):
        for a1 in range(29):
            for a2 in range(29):
                x=(a0*s[m]+a1*p1[m]+a2*p2[m])%29; res.append((ioc(x),a0,a1,a2))
    res.sort(reverse=True); print(mode,'n=%d'%m.sum(),res[:6])
